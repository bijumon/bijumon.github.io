// tag-filter.js (Unified logic for both single post and index pages)

document.addEventListener('DOMContentLoaded', () => {
    const TAG_DATA_URL = '/tags_data.json';
    let allTagsData = {}; 

    // Find ALL tag list containers, regardless of where they are on the page.
    const allTagContainers = document.querySelectorAll('.tag-buttons-container');

    if (allTagContainers.length === 0) {
        return; // No filters to initialize
    }

    // --- 1. Fetch Global Tag Data ---
    fetch(TAG_DATA_URL)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch ${TAG_DATA_URL}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            allTagsData = data;
            
            // --- 2. Initialize Filter for EVERY container found ---
            allTagContainers.forEach(tagContainer => {
                // The parent element (article or page content) is the scope for finding the results container
                const scopeElement = tagContainer.closest('article.post') || document.body;
                
                // Find the corresponding results container using its specific class
                const postsListContainer = scopeElement.querySelector('.posts-list-container');
                
                if (postsListContainer) {
                    initializeFilterInstance(tagContainer, postsListContainer);
                }
            });
        })
        .catch(error => {
            console.error('Error fetching or parsing tag data:', error);
            // This error handling is now only for the data fetch, not per-instance.
            allTagContainers.forEach(container => {
                const scope = container.closest('article.post') || document.body;
                scope.querySelector('.posts-list-container').innerHTML = '<p class="error">Could not load tag data for filtering.</p>';
            });
        });

    // --- 3. Core Logic: Setup listeners and handlers for one instance ---
    function initializeFilterInstance(tagButtonsContainer, postsListContainer) {
        
        const tagButtons = tagButtonsContainer.querySelectorAll('.tag-button');
        
        // Initial Message
        postsListContainer.innerHTML = '';

        // Attach event listeners
        tagButtons.forEach(btn => {
            // Use an anonymous function to wrap the handler and pass the necessary scope
            btn.addEventListener('click', (event) => handleTagClick(event, tagButtons, postsListContainer));
            btn.addEventListener('keypress', (event) => handleKeyPress(event, tagButtons, postsListContainer));
        });
    }
    
    // --- Accessibility: Handle Enter/Space key presses ---
    function handleKeyPress(event, tagButtons, postsListContainer) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleTagClick(event, tagButtons, postsListContainer);
        }
    }


    // --- 4. Handle Tag Click Event (Toggle Logic) ---
    function handleTagClick(event, tagButtons, postsListContainer) {
        const clickedButton = event.currentTarget;
        const selectedTag = clickedButton.dataset.tag;
        
        const isCurrentlyActive = clickedButton.classList.contains('active');

        // Remove active class from ALL buttons within this specific instance
        tagButtons.forEach(btn => {
            btn.classList.remove('active');
        });

        if (isCurrentlyActive) {
            // Toggling OFF: Clear the results
            postsListContainer.innerHTML = '';
            return; 
        }

        // Toggling ON: Set the clicked button as active
        clickedButton.classList.add('active');

        // Filter and Display Posts
        let postsToShow = allTagsData[selectedTag] || [];
        
        // Get the current page's URL to exclude the post itself
        const currentPostUrl = window.location.pathname; 
        postsToShow = postsToShow.filter(post => post.url !== currentPostUrl);

        displayPosts(postsToShow, selectedTag, postsListContainer);
    }

    // --- 5. Display Post Links ---
    function displayPosts(posts, tag, resultsContainer) {
        resultsContainer.innerHTML = ''; 
        
        if (posts.length === 0) {
            resultsContainer.innerHTML = `<p>No *other* related posts found for the tag: <strong>${tag.replace(/-/g, ' ')}</strong>.</p>`;
            return;
        }

        const ul = document.createElement('ul');
        posts.forEach(post => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            
            a.href = post.url;
            a.textContent = post.title;
            
            const summary = document.createElement('p');
            summary.classList.add('post-summary');
            summary.textContent = post.excerpt;
            
            li.appendChild(a);
            li.appendChild(summary);
            ul.appendChild(li);
        });

        resultsContainer.appendChild(ul);
        resultsContainer.focus();
    }
});