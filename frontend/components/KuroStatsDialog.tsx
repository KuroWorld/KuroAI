import React from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { Cat, Battery, Brain, PlayCircle, HeartPulse } from 'lucide-react'

interface KuroStatsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const KuroStatsDialog = ({ open, onOpenChange }: KuroStatsDialogProps) => {
  const stats = {
    activity: "Napping in the sun",
    mood: "Happy",
    energy: 60,
    thoughts: "I wonder what adventure awaits me today!"
  }

  const getMoodEmoji = (mood: string) => {
    switch (mood) {
      case "Ecstatic": return "😺"
      case "Happy": return "😸"
      case "Content": return "😺"
      case "Curious": return "🙀"
      case "Playful": return "😽"
      case "Sleepy": return "😴"
      case "Grumpy": return "😾"
      default: return "😺"
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px] bg-slate-800 text-slate-100">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-yellow-400 flex items-center gap-2">
            <Cat className="w-6 h-6" />
            Kuro's Status
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-700/50 p-3 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <PlayCircle className="w-5 h-5 text-blue-400" />
                <span className="text-sm font-medium text-slate-200">Activity</span>
              </div>
              <p className="text-sm text-slate-300">{stats.activity}</p>
            </div>
            <div className="bg-slate-700/50 p-3 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <HeartPulse className="w-5 h-5 text-red-400" />
                <span className="text-sm font-medium text-slate-200">Mood</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-slate-300">{stats.mood}</span>
                <span className="text-2xl" role="img" aria-label={`Mood: ${stats.mood}`}>
                  {getMoodEmoji(stats.mood)}
                </span>
              </div>
            </div>
          </div>
          <div className="bg-slate-700/50 p-3 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center gap-2">
                <Battery className="w-5 h-5 text-yellow-400" />
                <span className="text-sm font-medium text-slate-200">Energy</span>
              </div>
              <span className="text-sm text-slate-300">{stats.energy}%</span>
            </div>
            <Progress value={stats.energy} className="h-2" />
          </div>
          <div className="bg-slate-700/50 p-3 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-5 h-5 text-purple-400" />
              <span className="text-sm font-medium text-slate-200">Kuro's Thoughts</span>
            </div>
            <p className="text-sm text-slate-300 italic">
              "{stats.thoughts}"
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default KuroStatsDialog
