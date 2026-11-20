import { useState } from "react";
import Input from "../../components/Input";
import Select from "../../components/Select";
import Button from "../../components/Button";

function CatererForm() {
  const [formData, setFormData] = useState({
    businessName: "",
    description: "",
    category: "",
    location: "",
    phone: "",
    email: "",
    menu: "",
  });

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData({
      ...formData,
      [name]: value,
    });
  }

  function handleSubmit(event) {
    event.preventDefault();
    console.log("Caterer Details:", formData);
    alert("Caterer details saved successfully!");
  }

  return (
    <div className="page-container">
      <h1>Caterer Profile</h1>
      <p>Add or update your catering business details.</p>

      <form onSubmit={handleSubmit}>
        <Input
          label="Business Name"
          name="businessName"
          value={formData.businessName}
          onChange={handleChange}
          placeholder="Enter business name"
        />

        <div className="form-group">
          <label htmlFor="description">Business Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Describe your catering services"
          />
        </div>

        <Select
          label="Catering Category"
          name="category"
          value={formData.category}
          onChange={handleChange}
          options={[
            { value: "wedding", label: "Wedding" },
            { value: "corporate", label: "Corporate Events" },
            { value: "birthday", label: "Birthday Parties" },
            { value: "private", label: "Private Events" },
          ]}
        />

        <Input
          label="Business Location"
          name="location"
          value={formData.location}
          onChange={handleChange}
          placeholder="Enter business location"
        />

        <Input
          label="Phone Number"
          name="phone"
          type="tel"
          value={formData.phone}
          onChange={handleChange}
          placeholder="Enter phone number"
        />

        <Input
          label="Email Address"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="Enter email address"
        />

        <div className="form-group">
          <label htmlFor="menu">Menu Information</label>
          <textarea
            id="menu"
            name="menu"
            value={formData.menu}
            onChange={handleChange}
            placeholder="Describe your menu and packages"
          />
        </div>

        <Button type="submit">Save Caterer Details</Button>
      </form>
    </div>
  );
}

export default CatererForm;