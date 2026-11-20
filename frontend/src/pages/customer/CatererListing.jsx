import { Link } from "react-router-dom";

const caterers = [
  {
    id: 1,
    name: "Elegant Events Catering",
    description: "Professional catering for weddings and private events.",
  },
  {
    id: 2,
    name: "Delicious Moments",
    description: "Quality meals for birthdays and corporate events.",
  },
  {
    id: 3,
    name: "Perfect Plates",
    description: "Fresh food and catering for every occasion.",
  },
];

function CatererListing() {
  return (
    <div className="page-container">
      <h1>Find the Perfect Caterer</h1>
      <p>Explore trusted catering services for your special events.</p>

      <input type="text" placeholder="Search for caterers..." />
      <button>Search</button>

      <h2>Featured Caterers</h2>

      <div className="caterer-list">
        {caterers.map((caterer) => (
          <div className="caterer-card" key={caterer.id}>
            <h3>{caterer.name}</h3>
            <p>{caterer.description}</p>
            <Link to={`/caterer/${caterer.id}`}>
              <button>View Details</button>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CatererListing;