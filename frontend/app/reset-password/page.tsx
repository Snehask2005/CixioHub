"use client"

import { useState }
from "react"

import { useRouter }
from "next/navigation"

import { resetPassword }
from "@/services/auth"
import Link from "next/dist/client/link"


export default function ResetPasswordPage() {

  const router = useRouter()

  const [password, setPassword] =
    useState("")

  const [loading, setLoading] =
    useState(false)

  const [message, setMessage] =
    useState("")

  const [error, setError] =
    useState("")


  async function handleResetPassword(
    e: React.FormEvent
  ) {

    e.preventDefault()

    setLoading(true)

    setError("")

    setMessage("")

    try {

      const email =
        localStorage.getItem(
          "reset_email"
        )

      if (!email) {

        setError(
          "Email missing"
        )

        return
      }

      const data =
        await resetPassword(
          email,
          password
        )

      if (
        data.message ===
        "Password reset successful"
      ) {

        setMessage(
          data.message
        )

        localStorage.removeItem(
          "reset_email"
        )

        setTimeout(() => {

          router.push(
            "/login"
          )

        }, 1500)

      } else {

        setError(
          data.message
        )
      }

    } catch {

      setError(
        "Password reset failed"
      )

    } finally {

      setLoading(false)
    }
  }


  return (

    <div className="min-h-screen flex items-center justify-center bg-gray-200">

      <form
        onSubmit={handleResetPassword}
        className="bg-white p-8 rounded-xl shadow-md w-full max-w-md"
      >

        <h1 className="text-3xl font-bold mb-6 text-center text-black">
          Reset Password
        </h1>

        <input
          type="password"
          placeholder="Enter new password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
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
            ? "Resetting..."
            : "Reset Password"}

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