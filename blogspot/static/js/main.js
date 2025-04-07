// Handle like button clicks
document.addEventListener('DOMContentLoaded', function() {
    // Initialize like buttons
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            fetch(`/post/${postId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.classList.toggle('active', data.liked);
                    this.querySelector('.like-count').textContent = data.likes_count;
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

// Image preview for create post
function previewImages() {
    const preview = document.querySelector('.image-preview');
    const files = document.querySelector('input[type=file]').files;

    preview.innerHTML = '';
    
    function readAndPreview(file) {
        if (!/\.(jpe?g|png|gif)$/i.test(file.name)) return;

        const reader = new FileReader();
        
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'preview-image';
            preview.appendChild(img);
        }
        
        reader.readAsDataURL(file);
    }

    if (files) {
        Array.prototype.forEach.call(files, readAndPreview);
    }
}

// Initialize tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});
