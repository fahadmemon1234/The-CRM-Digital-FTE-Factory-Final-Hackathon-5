import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-neutral-950 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "bg-cyan-600 text-white shadow-lg hover:bg-cyan-700 hover:shadow-cyan-500/25",
        destructive:
          "bg-red-600 text-white shadow-lg hover:bg-red-700 hover:shadow-red-500/25",
        outline:
          "border border-neutral-700/50 bg-neutral-900/50 backdrop-blur-xl text-neutral-200 shadow-sm hover:bg-neutral-800/50 hover:border-neutral-600/50 hover:shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all duration-300",
        secondary:
          "bg-neutral-800 text-neutral-200 shadow-sm hover:bg-neutral-700",
        ghost: "hover:bg-neutral-800/50 hover:text-neutral-200 transition-all duration-200",
        link: "text-cyan-400 underline-offset-4 hover:underline",
        premium:
          "bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 text-white shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:shadow-[0_0_30px_rgba(6,182,212,0.6)] hover:scale-[1.02] border border-cyan-500/20",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-11 rounded-lg px-6 text-base",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
