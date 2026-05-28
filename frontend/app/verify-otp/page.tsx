"use client"

import {
  useEffect,
  useState
}
from "react"

import { useRouter }
from "next/navigation"

import {
  verifyOtp,
  forgotPassword
}
from "@/services/auth"

import Link from "next/dist/client/link"


export default function VerifyOtpPage() {

  const router = useRouter()

  const [otp, setOtp] =
    useState("")

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState("")
 
  const [timer, setTimer] =
  useState(30)

  const [canResend, setCanResend] =
  useState(false)

  useEffect(() => {

  if (timer > 0) {

    const interval =
      setInterval(() => {

        setTimer(
          (prev) => prev - 1
        )

      }, 1000)

    return () =>
      clearInterval(interval)

  } else {

    setCanResend(true)
  }

}, [timer])

  async function handleVerifyOtp(
    e: React.FormEvent
  ) {

    e.preventDefault()

    setLoading(true)

    setError("")

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
        await verifyOtp(
          email,
          otp
        )

      if (
        data.message ===
        "OTP verified successfully"
      ) {

        router.push(
          "/reset-password"
        )

      } else {

        setError(
          data.message
        )
      }

    } catch {

      setError(
        "OTP verification failed"
      )

    } finally {

      setLoading(false)
    }
  }
  async function handleResendOtp() {

  try {

    const email =
      localStorage.getItem(
        "reset_email"
      )

    if (!email) return

    await forgotPassword(email)

    setTimer(30)

    setCanResend(false)

  } catch {

    setError(
      "Failed to resend OTP"
    )
  }
}

  return (

    <div className="min-h-screen flex items-center justify-center bg-gray-200">

      <form
        onSubmit={handleVerifyOtp}
        className="bg-white p-8 rounded-xl shadow-md w-full max-w-md"
      >

        <h1 className="text-3xl font-bold mb-6 text-center text-black">
          Verify OTP
        </h1>

        <input
          type="text"
          placeholder="Enter OTP"
          value={otp}
          onChange={(e) =>
            setOtp(e.target.value)
          }
          className="w-full p-3 border border-gray-300 rounded-lg mb-4 text-black placeholder-gray-400 bg-white"
        />

        <div className="mb-4 text-center">

            {canResend ? (

            <button
                type="button"
                onClick={handleResendOtp}
                className="text-blue-600 hover:underline"
            >
                Resend OTP
            </button>

        ) : (

            <p className="text-gray-600">
                Resend OTP in {timer}s
            </p>

        )}

</div>

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
            ? "Verifying..."
            : "Verify OTP"}

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