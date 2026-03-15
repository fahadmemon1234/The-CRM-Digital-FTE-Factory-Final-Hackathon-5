import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:ring-offset-2 focus:ring-offset-neutral-950",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-cyan-600 text-white shadow-lg",
        secondary:
          "border-transparent bg-neutral-800 text-neutral-200 shadow-sm",
        destructive:
          "border-transparent bg-red-600 text-white shadow-lg",
        outline: 
          "border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl text-neutral-200",
        success:
          "border-emerald-500/30 bg-emerald-500/10 text-emerald-400 backdrop-blur-xl",
        warning:
          "border-amber-500/30 bg-amber-500/10 text-amber-400 backdrop-blur-xl",
        info:
          "border-cyan-500/30 bg-cyan-500/10 text-cyan-400 backdrop-blur-xl",
        premium:
          "border-purple-500/30 bg-purple-500/10 text-purple-400 backdrop-blur-xl",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
