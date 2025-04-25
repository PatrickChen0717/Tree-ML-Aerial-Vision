import React from 'react'

const englishToScientific = new Map([
  ["birch", "Betula"],
  ["oak", "Quercus"],
  ["spruce", "Picea"],
  ["maple", "Acer"],
  ["ash", "Fraxinus"],
  ["beech", "Fagus"],
  ["larch", "Larix"],
  ["elm", "Ulmus"],
  ["hophornbeam", "Ostrya"],
  ["aspen", "Populus"],
  ["pine", "Pinus"],
  ["hemlock", "Tsuga"],
  ["fir", "Abies"],
  ["cedar", "Thuja"],
  ["yellow birch", "Betula alleghaniensis"],
  ["white birch", "Betula papyrifera"],
  ["northern red oak", "Quercus rubra"],
  ["white spruce", "Picea glauca"],
  ["black spruce", "Picea mariana"],
  ["norway spruce", "Picea abies"],
  ["red spruce", "Picea rubens"],
  ["red maple", "Acer rubrum"],
  ["sugar maple", "Acer saccharum"],
  ["white ash", "Fraxinus americana"],
  ["american beech", "Fagus grandifolia"],
  ["eastern larch", "Larix laricina"],
  ["american elm", "Ulmus americana"],
  ["american hophornbeam", "Ostrya virginiana"],
  ["quaking aspen", "Populus tremuloides"],
  ["eastern white pine", "Pinus strobus"],
  ["red pine", "Pinus resinosa"],
  ["eastern hemlock", "Tsuga canadensis"],
  ["balsam fir", "Abies balsamea"],
  ["northern white cedar", "Thuja occidentalis"]
]);


const colorsGenus = [
  "#ef4444", // red-500
  "#facc15", // yellow-400
  "#22c55e", // green-500
  "#3b82f6", // blue-500
  "#ffffff", // white
  "#ec4899", // pink-500
  "#f97316", // orange-500
  "#14b8a6", // teal-500
  "#6366f1", // indigo-500
  "#84cc16", // lime-500
  "#f59e0b", // amber-500
  "#f43f5e"  // rose-500
];

const colorsSpecies = [
  "#dc2626", // red-600
  "#eab308", // yellow-500
  "#16a34a", // green-600
  "#ffffff", // white
  "#9333ea", // purple-600
  "#db2777", // pink-600
  "#ea580c", // orange-600
  "#0d9488", // teal-600
  "#4f46e5", // indigo-600
  "#65a30d", // lime-600
  "#d97706", // amber-600
  "#06b6d4", // cyan-600
  "#10b981", // emerald-600
  "#c026d3", // fuchsia-600
  "#0284c7", // sky-600
  "#7c3aed", // violet-600
  "#e11d48"  // rose-600
];

const classesSpecies = [
  "Pinus_sylvestris",
  "Fagus_sylvatica",
  "Picea_abies",
  "Cleared",
  "Quercus_robur",
  "Acer_pseudoplatanus",
  "Betula_spec.",
  "Pseudotsuga_menziesii",
  "Fraxinus_excelsior",
  "Quercus_petraea",
  "Alnus_spec.",
  "Quercus_rubra",
  "Larix_kaempferi",
  "Larix_decidua",
  "Abies_alba",
  "Pinus_strobus",
  "Pinus_nigra",
]

const classesGenus = [
  "Abies",
  "Acer",
  "Alnus",
  "Betula",
  "Cleared",
  "Fagus",
  "Fraxinus",
  "Larix",
  "Picea",
  "Pinus",
  "Pseudotsuga",
  "Quercus"
]

const classesGenusEnglish = [
  "Fir",
  "Maple",
  "Alder",
  "Birch",
  "Cleared",
  "Beech",
  "Ash",
  "Larch",
  "Spruce",
  "Pine",
  "Douglas-fir",
  "Oak"
]

const classesSpeciesEnglish = [
  "Scots pine",
  "European beech",
  "Norway spruce",
  "Cleared",
  "English oak",
  "Sycamore maple",
  "Birch species",
  "Douglas fir",
  "European ash",
  "Sessile oak",
  "Alder species",
  "Northern red oak",
  "Japanese larch",
  "European larch",
  "Silver fir",
  "Eastern white pine",
  "Black pine"
]

const CircleChart = ({ labelPercentage, genus, predictions, prediction, predictions_seg }) => {
  if (!labelPercentage && !predictions && !predictions_seg) return null;

  const radius = 100;
  const strokeWidth = 40;
  const center = radius + strokeWidth;
  const circumference = 2 * Math.PI * radius;

  let data = null

  if (labelPercentage) {
    data = Object.entries(labelPercentage).map(([label, percentage]) => ({
      label,
      value: Number(percentage),
      colour: genus
        ? colorsGenus[classesGenus.indexOf(label)]
        : colorsSpecies[classesSpecies.indexOf(label)],
    }));
  } else if (predictions_seg) {
    data = Object.entries(predictions_seg).map(([label, { percentage, colour }]) => ({
      label,
      value: Number(percentage),
      colour
    }));
  } else {
    data = predictions.map(([label, percentage], i) => ({
      label,
      value: Number(percentage),
      colour: colorsGenus[i]
    }));
  }

  data.sort((a, b) => b.value - a.value);

  const total = data.reduce((sum, item) => sum + item.value, 0);

  let rotation = 0;
  const donutSegments = data.map((item, i) => {
    const value = item.value;
    const offset = (value / total) * circumference;
    const strokeDasharray = `${offset} ${circumference - offset}`;
    const rotate = rotation;
    rotation += (value / total) * 360;

    return (
      <circle
        key={item.label}
        r={radius}
        cx={center}
        cy={center}
        fill="transparent"
        stroke={item.colour}
        strokeWidth={strokeWidth}
        strokeDasharray={strokeDasharray}
        strokeDashoffset={circumference / 4}
        transform={`rotate(${rotate} ${center} ${center})`}
      />
    );
  });

  return (
    <div className="flex flex-col items-center text-white">
      <div className="font-bold text-3xl self-center max-w-[80vw] text-center capitalize">{prediction}</div>
      <svg
        width={2 * (radius + strokeWidth)}
        height={2 * (radius + strokeWidth)}
        className="mb-4"
      >
        {donutSegments}
        <circle
          cx={center}
          cy={center}
          r={radius - strokeWidth / 2}
          fill="#357960"
        />
        <text
          x={center}
          y={center}
          textAnchor="middle"
          alignmentBaseline="middle"
          fill="white"
          fontSize="16"
          fontWeight="bold"
        >
          Results
        </text>
      </svg>

      <div className="flex flex-col items-start text-sm gap-6">
        {data.map((item, i) => (
          <div
            key={i}
            className="flex flex-row gap-2 max-w-[80vw]"
          >
            <div
              className="w-4 self-stretch rounded capitalize"
              style={{
                backgroundColor: item.colour,
              }}
            />
            {labelPercentage && (
              <div className="flex flex-row gap-1 font-bold whitespace-normal capitalize self-center leading-none py-2">
                {genus
                  ? (<>{classesGenusEnglish[classesGenus.indexOf(item.label)]} {item.label.toLowerCase() != 'cleared' && (<div className="italic capitalize"> ({item.label.replaceAll("_", " ").replaceAll(".", "")})</div>)}</>)
                  : (<>{classesSpeciesEnglish[classesSpecies.indexOf(item.label)]} {item.label.toLowerCase() != 'cleared' && (<div className="italic capitalize"> ({item.label.replaceAll("_", " ").replaceAll(".", "")})</div>)}</>)}
                : {item.value.toFixed(1)}%
              </div>
            )}
            {predictions && (
              <div className="flex flex-row gap-1 font-bold whitespace-normal capitalize self-center leading-none py-2">
                {item.label} <div className="italic">({englishToScientific.get(item.label)}):{" "}</div>
                {(item.value * 100).toFixed(1)}%
              </div>
            )}
            {predictions_seg && (
              <div className="flex flex-row gap-1 font-bold whitespace-normal capitalize self-center leading-none py-2">
                {item.label}:{" "}{(item.value).toFixed(2)}%
              </div>
            )}
          </div>
        ))}
      </div>

    </div>
  );
};

export default CircleChart;
