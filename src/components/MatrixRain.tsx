import React, { useEffect, useRef } from 'react';

export default function MatrixRain() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas dimensions to window dimensions
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Matrix characters (Binary + tech symbols)
    const characters = '0101010101010101<>{}[]!@#$%^&*~';
    const charArray = characters.split('');

    const fontSize = 14;
    let columns = canvas.width / fontSize;
    
    // Array of drops - one per column
    // Initialize drops to be randomly scattered across the vertical height initially
    const drops: number[] = [];
    for (let x = 0; x < columns; x++) {
      drops[x] = Math.random() * (canvas.height / fontSize) * -1; // Start off-screen randomly
    }

    const draw = () => {
      // Re-calculate columns in case of resize
      columns = canvas.width / fontSize;
      while (drops.length < columns) {
        drops.push(Math.random() * (canvas.height / fontSize) * -1);
      }

      // Semi-transparent black background to create trail effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Bright blue text color
      ctx.fillStyle = '#3b82f6'; // Bright blue (Tailwind blue-500)
      ctx.font = fontSize + 'px monospace';

      for (let i = 0; i < drops.length; i++) {
        // Random character
        const text = charArray[Math.floor(Math.random() * charArray.length)];
        
        // x coordinate of the drop, y coordinate
        const x = i * fontSize;
        const y = drops[i] * fontSize;

        // Draw the character
        ctx.fillText(text, x, y);

        // Reset drop to top randomly when it goes off screen
        if (y > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }

        // Increment y coordinate
        drops[i]++;
      }
    };

    const intervalId = setInterval(draw, 33); // ~30fps

    return () => {
      clearInterval(intervalId);
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  return (
    <canvas 
      ref={canvasRef} 
      className="fixed inset-0 z-0 opacity-30 pointer-events-none"
    />
  );
}
