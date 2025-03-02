document.addEventListener("DOMContentLoaded", function () {
    const cardContainer = document.querySelector(".card-container");

    // Function to add a new card
    function addCard(title, description, imageUrl, type, updatedTime) {
        const card = document.createElement("div");
        card.classList.add("card", type);

        const cardImage = document.createElement("div");
        cardImage.classList.add("card-image");
        cardImage.innerHTML = `<img src="${imageUrl}" alt="${title}">`;

        const cardContent = document.createElement("div");
        cardContent.classList.add("card-content");
        cardContent.innerHTML = `
            <h3 class="card-title">${title}</h3>
            <p class="card-description">${description}</p>
            <p class="card-updated-time">Updated: ${updatedTime}</p>
        `;

        card.appendChild(cardImage);
        card.appendChild(cardContent);
        cardContainer.appendChild(card);
    }

    // Example: Add a card dynamically (you can replace this with your logic)
    addCard(
        "Sample Title",
        "This is a sample card description.",
        "https://via.placeholder.com/300",
        "vertical",
        "2023-10-01"
    );
});