import { useState } from "react";
import Input from "../../components/Input";
import Select from "../../components/Select";
import Button from "../../components/Button";

function BookingForm() {
  const [formData, setFormData] = useState({
    customerName: "",
    eventType: "",
    eventDate: "",
    guests: "",
    location: "",
    phone: "",
    requirements: "",
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
    console.log("Booking Details:", formData);
    alert("Booking submitted successfully!");
  }

  return (
    <div className="page-container">
      <h1>Book Your Catering Service</h1>
      <p>Fill in the details below to request a booking.</p>

      <form onSubmit={handleSubmit}>
        <Input label="Customer Name" name="customerName" value={formData.customerName} onChange={handleChange} placeholder="Enter your name" />

        <Select
          label="Event Type"
          name="eventType"
          value={formData.eventType}
          onChange={handleChange}
          options={[
            { value: "wedding", label: "Wedding" },
            { value: "birthday", label: "Birthday" },
            { value: "corporate", label: "Corporate Event" },
            { value: "private", label: "Private Event" },
          ]}
        />

        <Input label="Event Date" name="eventDate" type="date" value={formData.eventDate} onChange={handleChange} />

        <Input label="Number of Guests" name="guests" type="number" value={formData.guests} onChange={handleChange} placeholder="Enter number of guests" />

        <Input label="Event Location" name="location" value={formData.location} onChange={handleChange} placeholder="Enter location" />

        <Input label="Phone Number" name="phone" type="tel" value={formData.phone} onChange={handleChange} placeholder="Enter phone number" />

        <div className="form-group">
          <label htmlFor="requirements">Special Requirements</label>
          <textarea
            id="requirements"
            name="requirements"
            value={formData.requirements}
            onChange={handleChange}
            placeholder="Any special requests?"
          />
        </div>

        <Button type="submit">Submit Booking</Button>
      </form>
    </div>
  );
}

export default BookingForm;