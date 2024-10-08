<script>
    import { onMount } from 'svelte';
    import { io } from 'socket.io-client';

    let urlInput = '';
    let updates = [];
    let htmlContent = '';
    let displayHtml = false;
    let isLoading = false;
    let toastMessage = '';
    let showToast = false;

    onMount(() => {
        const storedUpdates = localStorage.getItem('scrapingUpdates');
        if (storedUpdates) {
            updates = JSON.parse(storedUpdates);
        }

        const socket = io('http://127.0.0.1:5002');

        socket.on('scraping_update', function(data) {
            updates = [...updates, data];
            saveUpdatesToLocalStorage();
        });
    });

    function saveUpdatesToLocalStorage() {
        localStorage.setItem('scrapingUpdates', JSON.stringify(updates));
    }

    function showToastMessage(message) {
        toastMessage = message;
        showToast = true;
        setTimeout(() => showToast = false, 3000);
    }

    async function startScraping() {
        if (updates.some(update => update.url === urlInput)) {
            showToastMessage('URL already exists in the list.');
            return;
        }

        if (!isValidUrl(urlInput)) {
            showToastMessage('Invalid URL format.');
            return;
        }

        isLoading = true;
        try {
            const response = await fetch('http://127.0.0.1:5002/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: urlInput })
            });

            if (!response.ok) {
                showToastMessage('Failed to scrape the URL. Please check if it is valid.');
                return;
            }

            const data = await response.json();
            console.log(data);
        } catch (error) {
            console.error('Error:', error);
            showToastMessage('An error occurred during scraping.');
        } finally {
            isLoading = false;
        }
    }

    function isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch (_) {
            return false;
        }
    }

    async function viewPage(key) {
        try {
            const response = await fetch(`http://127.0.0.1:5002/page/${key}`);
            const contentType = response.headers.get('Content-Type');
            const content = await response.text();

            if (contentType.includes('html')) {
                htmlContent = content;
                displayHtml = true;
            } else if (contentType.includes('json')) {
                htmlContent = `<pre>${content}</pre>`;
                displayHtml = true;
            } else if (contentType.includes('xml') || contentType.includes('application/xml')) {
                htmlContent = `<pre>${content}</pre>`;
                displayHtml = true;
            } else if (contentType.includes('text')) {
                htmlContent = `<pre>${content}</pre>`;
                displayHtml = true;
            } else {
                console.error('Unsupported content type:', contentType);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    function removeUrl(index) {
        updates = updates.filter((_, i) => i !== index);
        saveUpdatesToLocalStorage();
    }

    function closeHtmlDisplay() {
        displayHtml = false;
        htmlContent = '';
    }
</script>

<div class="bg-gray-900 text-white min-h-screen flex flex-col items-center p-4">
    <img src="/image.png" alt="Shakescraper" class="w-80 h-32 mb-8">

    <form on:submit|preventDefault={startScraping} class="mb-8 w-full max-w-lg flex justify-center">
        <input
            type="text"
            bind:value={urlInput}
            placeholder="Enter URL to scrape"
            required
            class="input input-bordered input-primary w-2/3"
        />
        <button class="btn btn-primary ml-2 w-1/4" type="submit">Scrape</button>
    </form>

    <div class="flex justify-center items-center mb-8">
        {#if isLoading}
            <div class="spinner border-t-4 border-blue-500 rounded-full w-12 h-12"></div>
        {/if}
    </div>

    <ul class="space-y-4 w-full max-w-xl">
        {#each updates as update, index}
            <li class="bg-gray-800 p-4 rounded-lg flex justify-between items-center">
                <div>
                    <strong>URL:</strong> {update.url}<br />
                    <strong>Status:</strong> {update.status}
                </div>
                <div class="flex space-x-2">
                    {#if update.status === "scraping complete"}
                        <button class="btn btn-sm btn-secondary" on:click={() => viewPage(update.key)}>View Page</button>
                    {/if}
                    <button class="btn btn-sm btn-error" on:click={() => removeUrl(index)}>Remove</button>
                </div>
            </li>
        {/each}
    </ul>

    {#if displayHtml}
        <div class="mt-8 p-6 bg-gray-800 border border-gray-700 rounded-lg relative w-full">
            <button class="absolute top-2 right-2 btn btn-sm btn-error" on:click={closeHtmlDisplay}>Close</button>
            <h2 class="text-2xl font-bold mb-4">Scraped Content:</h2>
            <div class="prose max-w-full">
                {@html htmlContent}
            </div>
        </div>
    {/if}

    {#if showToast}
        <div class="fixed bottom-4 right-4 bg-red-600 text-white p-4 rounded-lg shadow-lg">
            {toastMessage}
        </div>
    {/if}
</div>

<style>
    .spinner {
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .transition-colors {
        transition: background-color 0.3s, color 0.3s;
    }
</style>
