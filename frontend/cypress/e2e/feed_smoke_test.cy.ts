describe("Feed Smoke Test", () => {
  it("successfully loads the homepage and displays the feed", () => {
    // Visit the homepage
    cy.visit("/");

    // Check if the main heading is visible
    cy.contains("h1", "Trading Calls Feed").should("be.visible");

    // Check if the feed container is present
    // It might be loading, but the container should be there.
    // We can also check for the loading text initially.
    cy.contains("Loading feed...").should("be.visible");

    // Wait for the feed to load (we can mock the API in a real scenario)
    // For this smoke test, we'll just wait for the loading text to disappear
    // and for at least one message card to appear.
    // The timeout can be adjusted based on expected network conditions.
    cy.get(".w-full.max-w-2xl > div", { timeout: 10000 }).should(
      "have.length.at.least",
      1
    );
  });
}); 