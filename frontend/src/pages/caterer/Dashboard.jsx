
const stats = [
  { label: "Total Bookings", value: "0", icon: "📅" },
  { label: "Pending Requests", value: "0", icon: "⏳" },
  { label: "Active Services", value: "0", icon: "🍽️" },
  { label: "Customer Enquiries", value: "0", icon: "💬" },
];

function Dashboard() {
  return (
    <main className="dashboard">
      <aside className="sidebar">
        <h2>Provider Portal</h2>

        <nav>
          <a href="#overview" className="active">Overview</a>
          <a href="#bookings">Bookings</a>
          <a href="#services">My Services</a>
          <a href="#enquiries">Enquiries</a>
          <a href="#profile">Business Profile</a>
        </nav>
      </aside>

      <section className="dashboard-content" id="overview">
        <div className="dashboard-header">
          <div>
            <span className="eyebrow">CATERER MANAGEMENT</span>
            <h1>Welcome to Your Dashboard</h1>
            <p>Manage your catering business from one place.</p>
          </div>
        </div>

        <div className="stats-grid">
          {stats.map((stat) => (
            <article className="stat-card" key={stat.label}>
              <span>{stat.icon}</span>
              <h3>{stat.value}</h3>
              <p>{stat.label}</p>
            </article>
          ))}
        </div>

        <section className="dashboard-panel" id="bookings">
          <h2>Recent Bookings</h2>
          <p>
            Your booking requests will appear here when
            customers start making enquiries.
          </p>
          <span className="empty-state">No bookings yet.</span>
        </section>
      </section>
    </main>
  );
}

export default Dashboard;
