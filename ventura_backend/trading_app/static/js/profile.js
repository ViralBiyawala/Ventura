import { hideAuthenticatedLinks, loadLogin } from './app.js';
import { fetchUserData, deleteUserData } from './api.js';

async function fetchProfile(token) {
    const response = await fetchUserData(token);
    return response;
}

async function deleteProfile(token) {
    const response = await deleteUserData(token);
    return response;
}

export function loadProfile() {
    const mainContent = document.getElementById('main-content');
    const token = localStorage.getItem('token');

    fetchProfile(token)
        .then(data => {
            mainContent.innerHTML = `
                <section class="profile-container card">
                    <header class="profile-header">
                        <h2 class="profile-title">User Profile</h2>
                    </header>
                    <div class="profile-details">
                        <p><strong>Username:</strong> ${data.username}</p>
                    </div>
                    <div class="profile-actions">
                        <button id="logout-button" class="btn btn-logout icon-button">Logout</button>
                        <button id="delete-profile-button" class="btn btn-delete icon-button">Delete Profile</button>
                    </div>
                </section>
            `;

            document.getElementById('logout-button').addEventListener('click', handleLogout);
            document.getElementById('delete-profile-button').addEventListener('click', handleDeleteProfile);
        })
        .catch(error => {
            alert('An error occurred: ' + error.message);
            handleLogout();
        });
}

export function handleDeleteProfile() {
    const token = localStorage.getItem('token');

    deleteProfile(token)
        .then(data => {
            if (data.success) {
                alert(data.message);
                handleLogout();
            } else {
                alert('Profile deletion failed: ' + data.message);
            }
        })
        .catch(error => {
            alert('An error occurred: ' + error.message);
            handleLogout();
        });
}

export async function handleLogout() {
    localStorage.removeItem('token');
    hideAuthenticatedLinks();
    loadLogin();
}

export { fetchProfile, deleteProfile };
