import { useEffect, useRef, useState } from 'react';
import { loadGameData } from './game/data';
import { TeaGardenWebGame } from './game/engine';

export default function App() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const gameRef = useRef<TeaGardenWebGame | null>(null);
  const [status, setStatus] = useState('Loading game data...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let disposed = false;

    const boot = async () => {
      try {
        const data = await loadGameData();
        if (disposed || !canvasRef.current) {
          return;
        }

        const game = new TeaGardenWebGame(canvasRef.current, data, setStatus);
        gameRef.current = game;
        game.start();
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown startup error';
        setError(message);
      }
    };

    void boot();

    return () => {
      disposed = true;
      gameRef.current?.stop();
    };
  }, []);

  return (
    <div className="app-shell">
      <div className="panel">
        <h1>Teabloom Garden — Web Port</h1>
        <p>{status}</p>
        {error ? <p className="error">{error}</p> : null}
      </div>
      <canvas ref={canvasRef} width={1024} height={768} className="game-canvas" />
    </div>
  );
}