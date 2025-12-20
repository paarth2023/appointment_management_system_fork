import * as React from "react"
import { cn } from "@/lib/utils"

const RadioGroupContext = React.createContext(null)

const RadioGroup = React.forwardRef(({ className, value, onValueChange, ...props }, ref) => {
  return (
    <RadioGroupContext.Provider value={{ value, onValueChange }}>
      <div className={cn("grid gap-2", className)} ref={ref} {...props} />
    </RadioGroupContext.Provider>
  )
})
RadioGroup.displayName = "RadioGroup"

const RadioGroupItem = React.forwardRef(({ className, value: itemValue, ...props }, ref) => {
  const context = React.useContext(RadioGroupContext)
  const isChecked = context?.value === itemValue

  const handleChange = () => {
    if (context?.onValueChange) {
      context.onValueChange(itemValue)
    }
  }

  return (
    <input
      type="radio"
      checked={isChecked}
      onChange={handleChange}
      className={cn(
        "aspect-square h-4 w-4 rounded-full border border-primary text-primary ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
RadioGroupItem.displayName = "RadioGroupItem"

export { RadioGroup, RadioGroupItem }

