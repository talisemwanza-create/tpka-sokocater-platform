function LoginRegister() {
  return (
    <div className="page-container">
      <h1>Welcome to SokoCater</h1>
      <p>Login or create an account to get started.</p>

      <section>
        <h2>Login</h2>
        <form>
          <label>Email Address</label>
          <input type="email" placeholder="Enter your email" />

          <label>Password</label>
          <input type="password" placeholder="Enter your password" />

          <button type="submit">Login</button>
        </form>
        <p>Don't have an account? Register below.</p>
      </section>

      <section>
        <h2>Register</h2>
        <form>
          <label>Full Name</label>
          <input type="text" placeholder="Enter your full name" />

          <label>Email Address</label>
          <input type="email" placeholder="Enter your email" />

          <label>Password</label>
          <input type="password" placeholder="Create a password" />

          <label>Confirm Password</label>
          <input type="password" placeholder="Confirm your password" />

          <button type="submit">Create Account</button>
        </form>
        <p>Already have an account? Login above.</p>
      </section>
    </div>
  );
}

export default LoginRegister;