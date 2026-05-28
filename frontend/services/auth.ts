import { apiRequest } from "./api"


export async function loginUser(
  email: string,
  password: string
) {

  return apiRequest(
    "/auth/login",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded"
      },

      body: new URLSearchParams({
        username: email,
        password
      })
    }
  )
}

export async function registerUser(
  email: string,
  full_name: string,
  password: string
) {

  return apiRequest(
    "/auth/register",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json"
      },

      body: JSON.stringify({
        email,
        full_name,
        password
      })
    }
  )
}

export async function forgotPassword(
  email: string
) {

  return apiRequest(
    "/auth/forgot-password",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json"
      },

      body: JSON.stringify({
        email
      })
    }
  )
}

export async function verifyOtp(
  email: string,
  otp: string
) {

  return apiRequest(
    "/auth/verify-otp",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json"
      },

      body: JSON.stringify({
        email,
        otp
      })
    }
  )
}

export async function resetPassword(
  email: string,
  new_password: string
) {

  return apiRequest(
    "/auth/reset-password",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json"
      },

      body: JSON.stringify({
        email,
        new_password
      })
    }
  )
}