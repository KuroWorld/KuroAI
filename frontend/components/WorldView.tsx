'use client'

import { useState, useEffect } from 'react'
import MapComponent from './Map'

export default function WorldView() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [weather, setWeather] = useState('sunny')
  const [currentEvent, setCurrentEvent] = useState("Kuro is exploring the neighborhood")
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  useEffect(() => {
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    // TODO: get this from the backend
    const weatherInterval = setInterval(() => {
      const weathers = ['sunny', 'partly cloudy', 'cloudy', 'light rain', 'heavy rain']
      setWeather(weathers[Math.floor(Math.random() * weathers.length)])
    }, 300000) // Change weather every 5 minutes

    const eventInterval = setInterval(() => {
      const events = [
        "Kuro is chasing butterflies in the park",
        "Kuro is napping in a sunny spot",
        "Kuro is watching birds from the window",
        "Kuro is playing with a ball of yarn",
        "Kuro is exploring the neighborhood"
      ]
      setCurrentEvent(events[Math.floor(Math.random() * events.length)])
    }, 60000) // Change event every minute

    return () => {
      clearInterval(timeInterval)
      clearInterval(weatherInterval)
      clearInterval(eventInterval)
    }
  }, [])

  return (
    <div className="space-y-4">
      <MapComponent currentEvent={currentEvent} weather={weather} />
    </div>
  )
}
