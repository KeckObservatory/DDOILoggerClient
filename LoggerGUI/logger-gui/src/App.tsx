import './App.css';
import { handleTheme } from './theme';
import CssBaseline from "@mui/material/CssBaseline";
import { TopBar } from './top_bar';
import { ThemeProvider } from "@mui/material/styles";
import { BooleanParam, useQueryParam, withDefault } from 'use-query-params'
import { LogView } from './log_view'

function App() {
  const [darkState, setDarkState] = useQueryParam('darkState', withDefault(BooleanParam, true));
  const theme = handleTheme(darkState)
  console.log('theme', theme)

  const handleThemeChange = (): void => {
    setDarkState(!darkState);
  }
  return (
    <ThemeProvider theme={theme} >
      <CssBaseline />
      <TopBar darkTheme={theme} handleThemeChange={handleThemeChange} />
      <LogView />
    </ThemeProvider>
  );
}

export default App;
