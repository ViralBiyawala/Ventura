#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <map>
#include "gym_anytrading_envs.h"
#include "indicators.h"
#include "price_updater.h"
#include "levels_calculator.h"
#include "investment_handler.h"
#include "balance_updater.h"
#include "metrics_calculator.h"
#include "report_generator.h"
#include "logging_config.h"
#include "models.h"

using namespace std;

struct TradeActionResult {
    int shares_held;
    double balance;
    double entry_price;
    int wins;
    int losses;
};

TradeActionResult execute_trade_action(int action, double current_price, double trade_amount, int shares_held, double balance, double entry_price, int wins, int losses, UserProfile user_profile, string symbol = "") {
    if (action == Actions::Buy && current_price > 0) {
        int shares_to_buy = !isnan(trade_amount / current_price) ? static_cast<int>(trade_amount / current_price) : 0;
        if (shares_to_buy > 0) {
            shares_held += shares_to_buy;
            balance -= (shares_to_buy * current_price);
            entry_price = current_price;
            logger.info("BUY " + to_string(shares_to_buy) + " shares at $" + to_string(current_price) + " | Balance: $" + to_string(balance));
            // Store the trade action in the database
            Trade::create(user_profile, symbol, "buy", current_price, shares_to_buy);
            // Update portfolio balance
            Portfolio portfolio = Portfolio::get(user_profile);
            portfolio.market_value -= (shares_to_buy * current_price);
            portfolio.save();
        } else {
            logger.info("HOLD (Insufficient funds to buy shares) | Current price: $" + to_string(current_price) + " | Balance: $" + to_string(balance));
        }
    } else if (action == Actions::Sell && shares_held > 0) {
        if (current_price > entry_price) {
            wins++;
        } else {
            losses++;
        }
        balance += (shares_held * current_price);
        logger.info("SELL " + to_string(shares_held) + " shares at $" + to_string(current_price) + " | Balance: $" + to_string(balance));
        // Store the trade action in the database
        Trade::create(user_profile, symbol, "sell", current_price, shares_held);
        // Update portfolio balance
        Portfolio portfolio = Portfolio::get(user_profile);
        portfolio.market_value += (shares_held * current_price);
        portfolio.save();
        shares_held = 0;
    }
    return {shares_held, balance, entry_price, wins, losses};
}

void execute_trades(Environment& env, Model& model, double initial_balance, double trade_fraction, string symbol, double stop_loss = 0.95, double take_profit = 1.05, string report_interval = "daily", int sptd = 390, bool enable_long_term_investment = true, UserProfile user_profile = UserProfile()) {
    double balance = initial_balance;
    vector<double> balance_history = {balance};
    int shares_held = 0;
    map<int, int> action_stats = {{Actions::Sell, 0}, {Actions::Buy, 0}};
    auto [observation, info] = env.reset(2021);
    double entry_price = 0;

    Portfolio portfolio = Portfolio::get(user_profile);
    portfolio.market_value += balance;
    portfolio.save();

    double long_term_fraction = enable_long_term_investment ? 1 - trade_fraction : 0;
    double long_term_investment = balance * long_term_fraction;
    int long_term_shares = 0;
    double rem_balance = 0;
    bool long_term_entry_done = false;

    balance -= long_term_investment;

    int wins = 0;
    int losses = 0;
    double peak_balance = balance;
    double max_drawdown = 0;
    double trade_amount = balance * trade_fraction;

    auto [atr, rsi] = initialize_indicators(env);

    while (true) {
        auto [action, _states] = model.predict(observation);
        double current_price = fetch_and_update_price(env, symbol);
        tie(observation, reward, terminated, truncated, info) = env.step(action);

        double current_atr = atr.average_true_range()[env.unwrapped().current_tick()];
        double current_rsi = rsi.rsi()[env.unwrapped().current_tick()];
        auto [dynamic_stop_loss, dynamic_take_profit] = calculate_dynamic_levels(current_price, current_atr, stop_loss, take_profit);

        tie(long_term_shares, long_term_entry_done, rem_balance) = handle_long_term_investment(enable_long_term_investment, long_term_entry_done, long_term_investment, current_price, long_term_shares, user_profile, symbol, rem_balance);

        trade_amount = balance * 0.9;

        if (shares_held > 0 && entry_price > 0) {
            if (current_price <= dynamic_stop_loss * entry_price) {
                logger.info("STOP-LOSS triggered. Selling " + to_string(shares_held) + " shares at $" + to_string(current_price));
                balance += (shares_held * current_price);
                losses++;
                portfolio = Portfolio::get(user_profile);
                portfolio.market_value += (shares_held * current_price);
                portfolio.save();
                shares_held = 0;
            } else if (current_price >= entry_price * dynamic_take_profit) {
                logger.info("TAKE-PROFIT triggered. Selling " + to_string(shares_held) + " shares at $" + to_string(current_price));
                balance += (shares_held * current_price);
                wins++;
                portfolio = Portfolio::get(user_profile);
                portfolio.market_value += (shares_held * current_price);
                portfolio.save();
                shares_held = 0;
            }
        }

        auto [new_shares_held, new_balance, new_entry_price, new_wins, new_losses] = execute_trade_action(action, current_price, trade_amount, shares_held, balance, entry_price, wins, losses, user_profile, symbol);
        shares_held = new_shares_held;
        balance = new_balance;
        entry_price = new_entry_price;
        wins = new_wins;
        losses = new_losses;
        action_stats[action]++;

        balance_history = update_balance_history(balance_history, balance);
        double total_balance_with_long_term = enable_long_term_investment ? balance + (long_term_shares * current_price) : balance;
        if (total_balance_with_long_term > peak_balance) {
            peak_balance = total_balance_with_long_term;
        }
        double drawdown = (peak_balance - total_balance_with_long_term) / peak_balance;
        if (drawdown > max_drawdown) {
            max_drawdown = drawdown;
        }

        if (terminated || truncated) {
            break;
        }
    }

    if (shares_held > 0) {
        balance += (shares_held * current_price);
        logger.info("Final SELL " + to_string(shares_held) + " shares at $" + to_string(current_price) + " | Balance: $" + to_string(balance));
        portfolio = Portfolio::get(user_profile);
        portfolio.market_value += (shares_held * current_price);
        portfolio.save();
    }

    if (enable_long_term_investment && long_term_shares > 0) {
        balance += (long_term_shares * current_price);
        balance += rem_balance;
        logger.info("Long-term SELL " + to_string(long_term_shares) + " shares at $" + to_string(current_price) + " | Balance: $" + to_string(balance));
        portfolio = Portfolio::get(user_profile);
        portfolio.market_value += (long_term_shares * current_price);
        portfolio.save();
    }

    auto [total_return, sharpe_ratio, win_loss_ratio] = calculate_metrics(balance_history, initial_balance, balance, wins, losses);

    logger.info("Total Return: " + to_string(total_return * 100) + "%");
    logger.info("Sharpe Ratio: " + to_string(sharpe_ratio));
    logger.info("Max Drawdown: " + to_string(max_drawdown * 100) + "%");
    logger.info("Win/Loss Ratio: " + to_string(win_loss_ratio));
    logger.info("Wins: " + to_string(wins) + ", Losses: " + to_string(losses));

    logger.info("Final Balance: $" + to_string(balance));
    logger.info("Action stats: " + to_string(action_stats));
    env.close();
}
