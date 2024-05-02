<script>
    import { goto } from '$app/navigation';
    
    function navigateToGame() {
      goto('/game');
    }
  </script>
  
  <style>
    
    main {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background-color: #ffad3b;
    }
    
    img {
      margin-bottom: 4rem;
    }
  
    button {
      background-color: white;
      border: none;
      padding: 0.8em 6em;
      border-radius: 100px;
      font-size: 1.5rem;
      cursor: pointer;
      transition: background-color 0.3s;
      font-family: 'Poppins', sans-serif; /* Add this line */
      font-weight: 900; /* Add this line */
    }
    
    button:hover {
      background-color: #f0f0f0;
    }
  </style>
  
  <main>
    <img src="/game.svg" alt="Game Logo">
    <button on:click={navigateToGame}>Start</button>
  </main>
  