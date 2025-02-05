import React from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { MapPin, Heart, MessageCircle, Clock } from 'lucide-react'

const AIAgentDialog = ({ open, onOpenChange, agent }) => {
  if (!agent) return null

  const relationshipLevel = Math.floor(Math.random() * 5) + 1
  const interactionCount = Math.floor(Math.random() * 100)
  const lastInteraction = Math.floor(Math.random() * 24) + 1

  const getRandomMood = () => {
    const moods = ["Happy", "Excited", "Curious", "Relaxed", "Busy", "Thoughtful"]
    return moods[Math.floor(Math.random() * moods.length)]
  }

  const getRandomActivity = () => {
    const activities = [
      "Reading a book",
      "Chatting with friends",
      "Working on a project",
      "Enjoying a coffee",
      "Taking a walk",
      "Shopping for groceries"
    ]
    return activities[Math.floor(Math.random() * activities.length)]
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px] bg-slate-800 text-slate-100">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-yellow-400">
            {agent.name}
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="bg-slate-700/50 p-3 rounded-lg">
            <h3 className="text-lg font-medium text-slate-200 mb-2 flex items-center">
              <Heart className="w-5 h-5 mr-2 text-red-400" />
              Relationship with Kuro
            </h3>
            <Progress value={relationshipLevel * 20} className="h-2 mb-2" />
            <p className="text-sm text-slate-300">Level {relationshipLevel} / 5</p>
          </div>
          <div className="bg-slate-700/50 p-3 rounded-lg">
            <h3 className="text-lg font-medium text-slate-200 mb-2 flex items-center">
              <MessageCircle className="w-5 h-5 mr-2 text-blue-400" />
              Interactions
            </h3>
            <p className="text-sm text-slate-300">Total interactions: {interactionCount}</p>
            <p className="text-sm text-slate-300">Last interaction: {lastInteraction} hours ago</p>
          </div>
          <div className="bg-slate-700/50 p-3 rounded-lg">
            <h3 className="text-lg font-medium text-slate-200 mb-2 flex items-center">
              <MapPin className="w-5 h-5 mr-2 text-green-400" />
              Current Location
            </h3>
            <p className="text-sm text-slate-300">{agent.location}</p>
          </div>
          <div className="bg-slate-700/50 p-3 rounded-lg">
            <h3 className="text-lg font-medium text-slate-200 mb-2 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-purple-400" />
              Current Status
            </h3>
            <p className="text-sm text-slate-300">Mood: {getRandomMood()}</p>
            <p className="text-sm text-slate-300">Activity: {getRandomActivity()}</p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default AIAgentDialog

