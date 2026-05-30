// Use relative URL since frontend and backend are on same server
const API_BASE = '';
let currentUser = null;
let authToken = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventListeners();
});

function checkAuth() {
    authToken = localStorage.getItem('authToken');
    if (authToken) {
        currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        showMainSection();
        loadFeed();
    } else {
        showAuthSection();
    }
}

function setupEventListeners() {
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('create-post-form').addEventListener('submit', handleCreatePost);
    document.getElementById('comment-form').addEventListener('submit', handleAddComment);
    document.getElementById('post-image').addEventListener('change', previewImage);
}

function showAuthSection() {
    document.getElementById('auth-section').style.display = 'flex';
    document.getElementById('main-section').style.display = 'none';
}

function showMainSection() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('main-section').style.display = 'block';
}

function switchTab(tab) {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const tabs = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(t => t.classList.remove('active'));
    
    if (tab === 'login') {
        tabs[0].classList.add('active');
        loginForm.style.display = 'flex';
        registerForm.style.display = 'none';
    } else {
        tabs[1].classList.add('active');
        loginForm.style.display = 'none';
        registerForm.style.display = 'flex';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = { user_id: data.user_id, username: data.username };
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showMainSection();
            loadFeed();
        } else {
            alert(data.detail || 'Login failed');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const bio = document.getElementById('register-bio').value;
    const profileImage = document.getElementById('register-profile-image').files[0];
    
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('email', email);
        formData.append('password', password);
        if (bio) formData.append('bio', bio);
        if (profileImage) formData.append('profile_image', profileImage);
        
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = { user_id: data.user_id, username: data.username };
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showMainSection();
            loadFeed();
        } else {
            alert(data.detail || 'Registration failed');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    authToken = null;
    currentUser = null;
    showAuthSection();
}

async function loadFeed() {
    try {
        const response = await fetch(`${API_BASE}/feed`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const posts = await response.json();
        displayPosts(posts, 'feed-posts');
    } catch (error) {
        console.error('Error loading feed:', error);
    }
}

function displayPosts(posts, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (posts.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 40px; color: #8e8e8e;">No posts yet. Follow users or create your first post!</p>';
        return;
    }
    
    posts.forEach(post => {
        const postCard = createPostCard(post);
        container.appendChild(postCard);
    });
}

function createPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    
    const timeAgo = getTimeAgo(new Date(post.created_at));
    
    card.innerHTML = `
        <div class="post-header">
            <img src="${post.profile_image_url || '/uploads/profiles/default.png'}" 
                 alt="${post.username}" 
                 class="post-profile-img"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2232%22 height=%2232%22%3E%3Ccircle cx=%2216%22 cy=%2216%22 r=%2215%22 fill=%22%23dbdbdb%22/%3E%3C/svg%3E'">
            <a href="#" onclick="viewUserProfile('${post.user_id}'); return false;" class="post-username">${post.username}</a>
        </div>
        <img src="${API_BASE}${post.image_url}" alt="Post" class="post-image" onclick="openPostModal('${post.post_id}')">
        <div class="post-actions">
            <button class="action-btn ${post.is_liked ? 'liked' : ''}" onclick="toggleLike('${post.post_id}', this)">
                ${post.is_liked ? '❤️' : '🤍'}
            </button>
            <button class="action-btn" onclick="openPostModal('${post.post_id}')">💬</button>
        </div>
        <div class="post-info">
            <div class="post-likes">${post.likes_count} likes</div>
            <div class="post-caption">
                <strong>${post.username}</strong> ${post.caption}
            </div>
            ${post.comments_count > 0 ? `<a href="#" class="post-comments-link" onclick="openPostModal('${post.post_id}'); return false;">View all ${post.comments_count} comments</a>` : ''}
            <div class="post-time">${timeAgo}</div>
        </div>
    `;
    
    return card;
}

async function toggleLike(postId, button) {
    try {
        const response = await fetch(`${API_BASE}/posts/${postId}/like`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const postCard = button.closest('.post-card');
            const likesElement = postCard.querySelector('.post-likes');
            const currentLikes = parseInt(likesElement.textContent);
            
            if (data.is_liked) {
                button.classList.add('liked');
                button.textContent = '❤️';
                likesElement.textContent = `${currentLikes + 1} likes`;
            } else {
                button.classList.remove('liked');
                button.textContent = '🤍';
                likesElement.textContent = `${currentLikes - 1} likes`;
            }
        }
    } catch (error) {
        console.error('Error toggling like:', error);
    }
}

function showFeed() {
    hideAllViews();
    document.getElementById('feed-view').style.display = 'block';
    loadFeed();
}

function showCreatePost() {
    hideAllViews();
    document.getElementById('create-post-view').style.display = 'block';
}

function showSearch() {
    hideAllViews();
    document.getElementById('search-view').style.display = 'block';
}

async function showProfile() {
    hideAllViews();
    document.getElementById('profile-view').style.display = 'block';
    await loadUserProfile(currentUser.user_id);
}

async function showNotifications() {
    hideAllViews();
    document.getElementById('notifications-view').style.display = 'block';
    await loadNotifications();
}

function hideAllViews() {
    document.querySelectorAll('.content-view').forEach(view => {
        view.style.display = 'none';
    });
}

function previewImage(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('post-image-preview').src = e.target.result;
            document.getElementById('post-image-preview').style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

async function handleCreatePost(e) {
    e.preventDefault();
    const image = document.getElementById('post-image').files[0];
    const caption = document.getElementById('post-caption').value;
    
    if (!image) {
        alert('Please select an image');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('image', image);
        formData.append('caption', caption);
        
        const response = await fetch(`${API_BASE}/posts`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Post created successfully!');
            document.getElementById('create-post-form').reset();
            document.getElementById('post-image-preview').style.display = 'none';
            showFeed();
        } else {
            alert(data.detail || 'Failed to create post');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function searchUsers() {
    const query = document.getElementById('search-input').value;
    if (query.length < 2) {
        document.getElementById('search-results').innerHTML = '';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/search/users?q=${encodeURIComponent(query)}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const users = await response.json();
        displaySearchResults(users);
    } catch (error) {
        console.error('Error searching users:', error);
    }
}

function displaySearchResults(users) {
    const container = document.getElementById('search-results');
    container.innerHTML = '';
    
    if (users.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 20px; color: #8e8e8e;">No users found</p>';
        return;
    }
    
    users.forEach(user => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.innerHTML = `
            <img src="${user.profile_image_url || '/uploads/profiles/default.png'}" 
                 alt="${user.username}"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2240%22 height=%2240%22%3E%3Ccircle cx=%2220%22 cy=%2220%22 r=%2219%22 fill=%22%23dbdbdb%22/%3E%3C/svg%3E'">
            <div>
                <strong>${user.username}</strong>
                ${user.bio ? `<div style="color: #8e8e8e; font-size: 14px;">${user.bio}</div>` : ''}
            </div>
        `;
        item.onclick = () => viewUserProfile(user.user_id);
        container.appendChild(item);
    });
}

async function viewUserProfile(userId) {
    hideAllViews();
    document.getElementById('profile-view').style.display = 'block';
    await loadUserProfile(userId);
}

async function loadUserProfile(userId) {
    try {
        const [profileResponse, postsResponse] = await Promise.all([
            fetch(`${API_BASE}/user/${userId}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            }),
            fetch(`${API_BASE}/user/${userId}/posts`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            })
        ]);
        
        const profile = await profileResponse.json();
        const posts = await postsResponse.json();
        
        displayProfile(profile, posts, userId);
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

function displayProfile(profile, posts, userId) {
    const container = document.getElementById('profile-content');
    
    const followButton = userId !== currentUser.user_id 
        ? `<button class="btn-primary" onclick="toggleFollow('${userId}')" id="follow-btn">${profile.is_following ? 'Unfollow' : 'Follow'}</button>`
        : '';
    
    container.innerHTML = `
        <div class="profile-container">
            <div class="profile-header">
                <img src="${profile.profile_image_url || '/uploads/profiles/default.png'}" 
                     alt="${profile.username}" 
                     class="profile-image-large"
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22150%22 height=%22150%22%3E%3Ccircle cx=%2275%22 cy=%2275%22 r=%2274%22 fill=%22%23dbdbdb%22/%3E%3C/svg%3E'">
                <div class="profile-info">
                    <h1>${profile.username}</h1>
                    <div class="profile-stats">
                        <div class="profile-stat">
                            <strong>${profile.posts_count}</strong>
                            <span>posts</span>
                        </div>
                        <div class="profile-stat">
                            <strong>${profile.followers_count}</strong>
                            <span>followers</span>
                        </div>
                        <div class="profile-stat">
                            <strong>${profile.following_count}</strong>
                            <span>following</span>
                        </div>
                    </div>
                    ${followButton}
                    ${profile.bio ? `<div class="profile-bio">${profile.bio}</div>` : ''}
                </div>
            </div>
            <div class="profile-posts-grid">
                ${posts.map(post => `
                    <div class="profile-post-item" onclick="openPostModal('${post.post_id}')">
                        <img src="${API_BASE}${post.image_url}" alt="Post">
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

async function toggleFollow(userId) {
    try {
        const response = await fetch(`${API_BASE}/follow/${userId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const btn = document.getElementById('follow-btn');
            if (btn) {
                btn.textContent = data.is_following ? 'Unfollow' : 'Follow';
            }
            loadUserProfile(userId);
        }
    } catch (error) {
        console.error('Error toggling follow:', error);
    }
}

async function openPostModal(postId) {
    document.getElementById('post-modal').style.display = 'flex';
    
    try {
        const [postResponse, commentsResponse] = await Promise.all([
            fetch(`${API_BASE}/feed`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            }),
            fetch(`${API_BASE}/posts/${postId}/comments`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            })
        ]);
        
        const posts = await postResponse.json();
        const comments = await commentsResponse.json();
        
        const post = posts.find(p => p.post_id === postId);
        
        if (post) {
            displayPostModal(post, comments, postId);
        }
    } catch (error) {
        console.error('Error loading post:', error);
    }
}

function displayPostModal(post, comments, postId) {
    const modalContent = document.getElementById('modal-post-content');
    const commentsContainer = document.getElementById('modal-comments');
    
    const timeAgo = getTimeAgo(new Date(post.created_at));
    
    modalContent.innerHTML = `
        <div class="post-header">
            <img src="${post.profile_image_url || '/uploads/profiles/default.png'}" 
                 alt="${post.username}" 
                 class="post-profile-img"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2232%22 height=%2232%22%3E%3Ccircle cx=%2216%22 cy=%2216%22 r=%2215%22 fill=%22%23dbdbdb%22/%3E%3C/svg%3E'">
            <a href="#" onclick="viewUserProfile('${post.user_id}'); return false;" class="post-username">${post.username}</a>
        </div>
        <img src="${API_BASE}${post.image_url}" alt="Post" style="width: 100%; margin: 10px 0;">
        <div class="post-actions">
            <button class="action-btn ${post.is_liked ? 'liked' : ''}" onclick="toggleLike('${post.post_id}', this)">
                ${post.is_liked ? '❤️' : '🤍'}
            </button>
        </div>
        <div class="post-info">
            <div class="post-likes">${post.likes_count} likes</div>
            <div class="post-caption">
                <strong>${post.username}</strong> ${post.caption}
            </div>
            <div class="post-time">${timeAgo}</div>
        </div>
    `;
    
    commentsContainer.innerHTML = comments.map(comment => `
        <div class="comment-item">
            <img src="${comment.profile_image_url || '/uploads/profiles/default.png'}" 
                 alt="${comment.username}"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2232%22 height=%2232%22%3E%3Ccircle cx=%2216%22 cy=%2216%22 r=%2215%22 fill=%22%23dbdbdb%22/%3E%3C/svg%3E'">
            <div class="comment-content">
                <strong>${comment.username}</strong>
                <div class="comment-text">${comment.comment_text}</div>
            </div>
        </div>
    `).join('');
    
    document.getElementById('comment-form').onsubmit = (e) => {
        e.preventDefault();
        handleAddComment(e, postId);
    };
}

function closePostModal() {
    document.getElementById('post-modal').style.display = 'none';
}

async function handleAddComment(e, postId) {
    e.preventDefault();
    const commentText = document.getElementById('comment-input').value;
    
    if (!commentText.trim()) return;
    
    try {
        const formData = new FormData();
        formData.append('comment_text', commentText);
        
        const response = await fetch(`${API_BASE}/posts/${postId}/comment`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            document.getElementById('comment-input').value = '';
            openPostModal(postId); // Reload modal
            loadFeed(); // Refresh feed
        }
    } catch (error) {
        console.error('Error adding comment:', error);
    }
}

async function loadNotifications() {
    try {
        const response = await fetch(`${API_BASE}/notifications`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const notifications = await response.json();
        displayNotifications(notifications);
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

function displayNotifications(notifications) {
    const container = document.getElementById('notifications-list');
    
    if (notifications.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 40px; color: #8e8e8e;">No notifications yet</p>';
        return;
    }
    
    container.innerHTML = notifications.map(notif => {
        const timeAgo = getTimeAgo(new Date(notif.created_at));
        let message = '';
        
        switch(notif.type) {
            case 'like':
                message = 'liked your post';
                break;
            case 'comment':
                message = 'commented on your post';
                break;
            case 'follow':
                message = 'started following you';
                break;
        }
        
        return `
            <div class="notification-item ${notif.is_read ? '' : 'unread'}">
                <img src="${notif.source_profile_image || '/uploads/profiles/default.png'}" 
                     alt="${notif.source_username}"
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2240%22 height=%2240%22%3E%3Ccircle cx=%2220%22 cy=%2220%22 r=%2219%22 fill=%22%23dbdbdb%22/%3E%3C/svg%3E'">
                <div>
                    <strong>${notif.source_username}</strong> ${message}
                    <div style="color: #8e8e8e; font-size: 12px; margin-top: 4px;">${timeAgo}</div>
                </div>
            </div>
        `;
    }).join('');
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
}

