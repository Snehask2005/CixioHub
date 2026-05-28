"use client"

import { useState }
from "react"

import { useRouter }
from "next/navigation"

import { registerUser }
from "@/services/auth"
import Link from "next/dist/client/link"


export default function RegisterPage() {

  const router = useRouter()

  const [email, setEmail] =
    useState("")

  const [full_name, setName] =
    useState("")

  const [password, setPassword] =
    useState("")


  const [error, setError] =
    useState("")

  const [loading, setLoading] =
    useState(false)


  async function handleRegister(
    e: React.FormEvent
  ) {

    e.preventDefault()

    setLoading(true)

    setError("")

    try {

      const data =
        await registerUser(
          email,
          full_name,
          password
        )

      if (data.email) {

        router.push("/login")

      } else {

        setError(
            typeof data.detail === "string"
                ? data.detail
                    : data.detail?.[0]?.msg ||
                        "Registration failed"
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
        onSubmit={handleRegister}
        className="bg-white p-8 rounded-xl shadow-md w-full max-w-md"
      >

        <h1 className="text-3xl font-bold mb-6 text-center text-black">
          Register
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
            type="text"
            placeholder="Full Name"
            value={full_name}
            onChange={(e) =>
                setName(e.target.value)
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
            ? "Creating Account..."
            : "Register"}

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