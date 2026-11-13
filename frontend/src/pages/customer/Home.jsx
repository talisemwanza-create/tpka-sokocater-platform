
const categories = [
  {
    name: "Food Catering",
    description: "Delicious meals for every occasion.",
    icon: "🍲",
  },
  {
    name: "Wedding Catering",
    description: "Make your special day memorable.",
    icon: "💍",
  },
  {
    name: "Corporate Events",
    description: "Professional catering for businesses.",
    icon: "🏢",
  },
  {
    name: "Private Parties",
    description: "Great food for your celebrations.",
    icon: "🎉",
  },
];

function Home() {
  return (
    <main>
      <section className="hero">
        <div className="hero-content">
          <p className="eyebrow">WELCOME TO SOKOCATER</p>
          <h1>Great Food. Perfect Events.</h1>
          <p>
            Discover trusted catering professionals for weddings,
            corporate events, parties, and more.
          </p>

          <div className="hero-actions">
            <a href="#categories" className="primary-button">
              Explore Catering
            </a>
            <a href="/caterer/dashboard" className="secondary-button">
              Become a Caterer
            </a>
          </div>
        </div>
      </section>

      <section className="categories" id="categories">
        <div className="section-heading">
          <p className="eyebrow">EXPLORE OUR SERVICES</p>
          <h2>Find Catering for Every Occasion</h2>
          <p>Choose the service that suits your event.</p>
        </div>

        <div className="category-grid">
          {categories.map((category) => (
            <article className="category-card" key={category.name}>
              <span className="category-icon">{category.icon}</span>
              <h3>{category.name}</h3>
              <p>{category.description}</p>
              <a href="#about">Explore services →</a>
            </article>
          ))}
        </div>
      </section>

      <section className="about" id="about">
        <div>
          <p className="eyebrow">ABOUT SOKOCATER</p>
          <h2>Connecting people with great catering.</h2>
          <p>
            SokoCater brings customers and catering businesses
            together through one convenient marketplace.
          </p>
        </div>
      </section>

      <footer className="footer">
        <p>© 2026 SokoCater. All rights reserved.</p>
      </footer>
    </main>
  );
}

export default Home;
