'use strict';

async function getCurrentUser() {
    // Fetches the current user from the backend
    try {
        const response = await axios.get('/get-current-user');
        return response.data;
    } catch (error) {
        console.error(error);
        return null;
    }
}

async function fetchProducts(searchQuery) {
    // Fetches products from the backend
    const search = { search: searchQuery };
    try {
        const response = await axios.get('/get-products', { params: search });
        return response.data;
    } catch (error) {
        alert(error.response.data.message)
    }
}

function toTitleCase(str) {
    // Converts a string to title case
    return str.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}

async function displayProducts(data) {
    // Displays products on the page
    $('#products').empty();
    const items =
        data.products.findItemsByKeywordsResponse[0].searchResult[0].item;
    for (let item of items) {
        const title = item.title[0];
        const imageURL = item.galleryURL[0];
        const currency = item.sellingStatus[0].currentPrice[0]['@currencyId'];
        const price = item.sellingStatus[0].currentPrice[0]['__value__'];
        const productURL = item.viewItemURL[0];
        const colElement = $(
            '<div class="col-12 col-sm-6 col-md-4 col-lg-3 mb-4"></div>'
        );
        const cardElement = $('<div class="card h-100"></div>');
        const imgElement = $(
            `<img src="${imageURL}" class="card-img-top img-fluid">`
        );
        const cardBodyElement = $('<div class="card-body"></div>');
        const titleElement = $(`<h5 class="card-title">${title}</h5>`);
        const priceElement = $(`<p class="card-text">${currency} ${price}</p>`);
        const linksContainer = $('<div class="d-flex gap-3"></div>');
        const linkElement = $(
            `<a href="${productURL}" target="_blank" class="btn btn-primary">Go to eBay</a>`
        );
        const addToWishlistLink = $(
            '<a href="#" class="btn btn-primary">Add to Wishlist</a>'
        );
        const product = {
            title,
            imageURL,
            currency,
            price,
            productURL,
        };
        addToWishlistLink.data('product', product); // Store the product data

        addToWishlistLink.click(async function () {
            const clickedProduct = $(this).data('product');
            // Store the product details somewhere (e.g., in a data attribute)
            $('#wishlistModal').data('selectedProduct', clickedProduct);
            // Fetch user's wishlists and populate the modal
            const currentUser = await getCurrentUser();
            const wishlists = currentUser.wishlists;
            $('#userWishlists').empty();
            if (wishlists.length > 0) {
                for (let wishlist of wishlists) {
                    $('#userWishlists').append(
                        `<li><a href="#" data-wishlist-name="${
                            wishlist.name
                        }">${toTitleCase(wishlist.name)}</a></li>`
                    );
                }
            } else {
                $('.modal-body').append(
                    `<p>You have no wishlists. Create one <a href="/users/${currentUser.userId}/wishlists/create">here!</a></p>`
                );
            }
            // Show the modal
            $('#wishlistModal').modal('show');
        });

        cardElement.append(imgElement);
        cardElement.append(cardBodyElement);
        cardBodyElement.append(titleElement);
        cardBodyElement.append(priceElement);
        cardBodyElement.append(linksContainer);
        linksContainer.append(linkElement);
        linksContainer.append(addToWishlistLink);
        colElement.append(cardElement);
        $('#products').append(colElement);
    }
}

$('#userWishlists').on('click', 'a', async function () {
    const selectedProduct = $('#wishlistModal').data('selectedProduct');
    const currentUser = await getCurrentUser();
    const wishlistName = $(this).data('wishlist-name'); // Assuming the wishlist name is stored in the data-wishlist-id attribute

    const url = `/users/${currentUser.userId}/wishlists/${wishlistName}/add-product`;

    try {
        const response = await axios.post(url, {
            wishlistName: wishlistName,
            product: selectedProduct,
        });
        // Handle the response if needed
        alert(response.data.message);
    } catch (error) {
        alert(error.response.data.message);
    }
});

$('#search-form').submit(async (event) => {
    // Handles the search form submission
    event.preventDefault();
    let $search = $('#search').val();
    const data = await fetchProducts($search);
    displayProducts(data);
});
