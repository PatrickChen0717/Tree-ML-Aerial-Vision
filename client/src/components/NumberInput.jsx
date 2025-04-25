import React from 'react'

const NumberInput = ({ numberInput, setNumberInput, title, units, integersOnly = false }) => {
  const handleNumberChange = (event) => {
    const value = event.target.value;

    if (value === "" || (!integersOnly && (value === "." || value === "-."))) {
      setNumberInput(value);
    } else {
      const pattern = integersOnly ? /^-?\d+$/ : /^-?\d*\.?\d*$/;
      if (pattern.test(value)) {
        setNumberInput(value);
      }
    }
  };

  return (
    <div className="self-center">
      <div className="flex flex-col bg-black/50 border-white border-[3px] rounded-3xl px-6 pb-4 pt-2 gap-2">
        <label className="text-white">{title}</label>
        <div className='flex flex-row justify-center items-center gap-2 text-primary bg-white overflow-hidden rounded-full px-4 w-min whitespace-nowrap self-center'>
          <input
            type="text"
            value={numberInput}
            onChange={handleNumberChange}
            className={`py-2 outline-none focus:ring-0 focus:outline-none focus:shadow-none text-primary ${units ? 'w-16' : 'w-32'}`}
            inputMode={integersOnly ? "numeric" : "decimal"}
            pattern={integersOnly ? "^-?\\d+$" : "^-?\\d*\\.?\\d*$"}
          />
          {units}
        </div>
      </div>
    </div>
  )
}

export default NumberInput
