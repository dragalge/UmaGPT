export interface Theme {
  id: string;
  label: string;
  primary: string;
  secondary: string;
}

export const Themes: Theme[] = [
  { id: "default", label: "Default", primary: "#5ec00c", secondary: "#FF3376" },
  { id: "1", label: "Special Week", primary: "#EE6DCB", secondary: "#FFDEF9" },
  { id: "2", label: "Silence Suzuka", primary: "#29BD70", secondary: "#FFCE48" },
  { id: "3", label: "Tokai Teio", primary: "#3376D2", secondary: "#FFCD00" },
  { id: "4", label: "Maruzensky", primary: "#EA504A", secondary: "#FFCD00" },
  { id: "5", label: "Fuji Kiseki", primary: "#444745", secondary: "#33B839" },
  { id: "6", label: "Oguri Cap", primary: "#3A7AD2", secondary: "#ECE7E7" },
  { id: "7", label: "Grass Wonder", primary: "#3A34AC", secondary: "#E3493F" },
  { id: "8", label: "Agnes Tachyon", primary: "#35B2B6", secondary: "#E2E868" },
];