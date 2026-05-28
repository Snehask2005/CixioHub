"use client"

import { useState }
from "react"

import { useRouter }
from "next/navigation"

import { forgotPassword }
from "@/services/auth"
import Link from "next/dist/client/link"


export default function ForgotPasswordPage() {

  const router = useRouter()

  const [email, setEmail] =
    useState("")

  const [loading, setLoading] =
    useState(false)

  const [message, setMessage] =
    useState("")

  const [error, setError] =
    useState("")


  async function handleForgotPassword(
    e: React.FormEvent
  ) {

    e.preventDefault()

    setLoading(true)

    setError("")

    setMessage("")

    try {

      const data =
        await forgotPassword(email)

      if (data.message) {

        setMessage(data.message)

        localStorage.setItem(
          "reset_email",
          email
        )

        setTimeout(() => {

          router.push(
            "/verify-otp"
          )

        }, 1500)

      }

    } catch {

      setError(
        "Failed to send OTP"
      )

    } finally {

      setLoading(false)
    }
  }


  return (

    <div className="min-h-screen flex items-center justify-center bg-gray-200">

      <form
        onSubmit={handleForgotPassword}
        className="bg-white p-8 rounded-xl shadow-md w-full max-w-md"
      >

        <h1 className="text-3xl font-bold mb-6 text-center text-black">
          Forgot Password
        </h1>

        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
          className="w-full p-3 border border-gray-300 rounded-lg mb-4 text-black placeholder-gray-400 bg-white"
        />

        {message && (
          <p className="text-green-600 mb-4">
            {message}
          </p>
        )}

        {error && (
          <p className="text-red-500 mb-4">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-black text-white p-3 rounded-lg"
        >

          {loading
            ? "Sending OTP..."
            : "Send OTP"}

        </button>

        <Link
            href="/login"
            className="text-blue-600 hover:underline"
        >
            Login
        </Link>

      </form>

    </div>
  )
}