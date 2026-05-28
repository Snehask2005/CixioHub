"use client"

import { useState } from "react"

import { useRouter } from "next/navigation"

import { loginUser } from "@/services/auth"

import Link from "next/link"


export default function LoginPage() {

  const router = useRouter()

  const [email, setEmail] =
    useState("")

  const [password, setPassword] =
    useState("")

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState("")


  async function handleLogin(
    e: React.FormEvent
  ) {

    e.preventDefault()

    setLoading(true)

    setError("")

    try {

      const data =
        await loginUser(
          email,
          password
        )

      if (data.access_token) {

        document.cookie =
          `access_token=${data.access_token}; path=/`

        document.cookie =
          `refresh_token=${data.refresh_token}; path=/`

        router.push(
          "/dashboard"
        )

      } else {

        setError(
          "Invalid credentials"
        )
      }

    } catch {

      setError(
        "Something went wrong"
      )

    } finally {

      setLoading(false)
    }
  }


  return (

    <div className="min-h-screen flex items-center justify-center bg-gray-200">

      <form
        onSubmit={handleLogin}
        className="bg-white p-8 rounded-xl shadow-md w-full max-w-md"
      >

        <h1 className="text-3xl font-bold mb-6 text-center text-black">
          Login
        </h1>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
          className="w-full p-3 border border-gray-300 rounded-lg mb-4 text-black placeholder-gray-400 bg-white"
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
          className="w-full p-3 border border-gray-300 rounded-lg mb-4 text-black placeholder-gray-400 bg-white"
        />

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
            ? "Logging in..."
            : "Login"}

        </button>

        <div className="mt-4 text-center">

      <div className="mt-2 text-center">

      <Link
        href="/register"
        className="text-blue-600 hover:underline"
      >
        New user?Create an account
      </Link>

</div>

      <Link
        href="/forgot-password"
        className="text-blue-600 hover:underline"
      >
        Forgot Password?
      </Link>

</div>

      </form>

    </div>
  )
}