import { XCircle } from "lucide-react";

export default function SignupForm({
  formData,
  errors,
  loading,
  onChange,
  onSubmit,
}) {
  return (
    <form onSubmit={onSubmit}>
      {/* Full Name */}
      <div className="row">
        <div className="col">
          <label>Full Name</label>
          <input
            type="text"
            name="full_name"
            value={formData.full_name}
            onChange={onChange}
            placeholder="Nguyen Van A"
            className={errors.full_name ? 'error' : ''}
          />
          {errors.full_name && (
            <span className="error-text">
              <XCircle className="error-icon-small" />
              {errors.full_name}
            </span>
          )}
        </div>
      </div>

      {/* Email */}
      <div className="row">
        <div className="col">
          <label>Email</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={onChange}
            placeholder="email@example.com"
            className={errors.email ? 'error' : ''}
          />
          {errors.email && (
            <span className="error-text">
              <XCircle className="error-icon-small" />
              {errors.email}
            </span>
          )}
        </div>
      </div>

      {/* Phone Number */}
      <div className="row">
        <div className="col">
          <label>Phone</label>
          <input
            type="tel"
            name="phone_num"
            value={formData.phone_num}
            onChange={onChange}
            placeholder="0901234567"
            className={errors.phone_num ? 'error' : ''}
          />
          {errors.phone_num && (
            <span className="error-text">
              <XCircle className="error-icon-small" />
              {errors.phone_num}
            </span>
          )}
        </div>
      </div>

      {/* Gender */}
      <div className="row">
        <div className="col">
          <label>Gender</label>
          <select
            name="gender"
            value={formData.gender}
            onChange={onChange}
            className={errors.gender ? 'error' : ''}
          >
            <option value="" disabled>--Choose your gender--</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
          {errors.gender && (
            <span className="error-text">
              <XCircle className="error-icon-small" />
              {errors.gender}
            </span>
          )}
        </div>
      </div>

      {/* Date of Birth */}
      <div className="row">
        <div className="col">
          <label>Date of Birth</label>
          <input
            type="date"
            name="date_of_birth"
            value={formData.date_of_birth}
            onChange={onChange}
            className={errors.date_of_birth ? 'error' : ''}
          />
          {errors.date_of_birth && (
            <span className="error-text">
              <XCircle className="error-icon-small" />
              {errors.date_of_birth}
            </span>
          )}
        </div>
      </div>

      {/* Address */}
      <div className="row">
        <div className="col">
          <label>Address</label>
          <input
            type="text"
            name="address"
            value={formData.address}
            onChange={onChange}
            placeholder="123 Example Street, City, Country"
            className={errors.address ? 'error' : ''}
          />
          {errors.address && (
            <span className="error-text">
              <XCircle className="error-icon-small" />
              {errors.address}
            </span>
          )}
        </div>
      </div>

      {/* Password */}
      <div className="row">
        <div className="col">
          <label>Password</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={onChange}
            placeholder="Password (at least 8 characters)"
            className={errors.password ? 'error' : ''}
          />
          {errors.password && (
            <span className="error-text">
              <XCircle className="error-icon-small" />
              {errors.password}
            </span>
          )}
        </div>
      </div>

      {/* Confirm Password */}
      <div className="row">
        <div className="col">
          <label>Confirm Password</label>
          <input
            type="password"
            name="password_confirm"
            value={formData.password_confirm}
            onChange={onChange}
            placeholder="Confirm password"
            className={errors.password_confirm ? 'error' : ''}
          />
          {errors.password_confirm && (
            <span className="error-text">
              <XCircle className="error-icon-small" />
              {errors.password_confirm}
            </span>
          )}
        </div>
      </div>

      {/* Terms Checkbox */}
      <div className="row">
        <div className="col">
          <label className="checkbox">
            <input
              type="checkbox"
              name="termsAccepted"
              checked={formData.termsAccepted}
              onChange={onChange}
            />
            <span>
              I agree to the <b>Terms of Service and Privacy Policy</b>, including HIPAA authorization
            </span>
          </label>
          {errors.termsAccepted && (
            <span className="error-text">
              <XCircle className="error-icon-small" />
              {errors.termsAccepted}
            </span>
          )}
        </div>
      </div>

      {/* Submit Button */}
      <button type="submit" className="btn-primary" disabled={loading}>
        {loading ? 'Processing...' : 'Create Account'}
      </button>
    </form>
  );
}

