<script>
  import { onMount } from 'svelte';

  let name = "Tasse 1";
  let countdown = 3;
  let showButton = true;
  let showDrink = false;
  let cups = [
    { id: 1, color: 'white' },
    { id: 2, color: 'white' },
    { id: 3, color: 'white' },
    { id: 4, color: 'white' },
  ];

  onMount(async () => {
    setInterval(async () => {
      for (let cup of cups) {
        const response = await fetch(`http://localhost:5000/get_cup_state?cup_id=${cup.id}`);
        const color = await response.text();
        cup.color = color;
      }
    }, 100);
  });

  async function startGame() {
    //const response = await fetch('http://localhost:5000/start_game');
    //const data = await response.json();
    //console.log(data);
    showButton = false;
    const countdownInterval = setInterval(() => {
      countdown -= 1;
      if (countdown === 0) {
        clearInterval(countdownInterval);
        showDrink = true;
      }
    }, 1000);
  }
</script>

<style>
  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
    background-color: #ffad3b;
  }

  .card {
    background-color: rgba(255, 255, 255, 0.5);
    border-radius: 15px;
    padding: 20px;
    width: 300px;
    margin: auto;
    text-align: center;
  }

  .card-container {
    display: flex;
    flex-direction: row;
    justify-content: center;
    margin-top: 5em;
    gap: 20px;
  }

  .card.white {
    background-color: rgba(255, 255, 255, 0.5);
  }

  .card.green {
    background-color: rgba(97, 255, 97, 0.5);
  }

  .card.red {
    background-color: rgba(255, 57, 57, 0.5);
  }

  h1 {
    margin-top: 1em;
    font-size: 50pt;
    color: white;
  }

  h2 {
    margin-top: 0em;
    margin-bottom: 0em;
    font-size: 40pt;
    color: white;
  }

  h3 {
    font-size: 25pt;
    color: black;
  }

  button {
      background-color: white;
      border: none;
      padding: 0.8em 4em;
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

    img {
    width: 20rem; /* adjust as needed */
    height: auto;
    margin-top: 0rem;
    margin-bottom: 2rem;
  }

</style>

<main>
  <img src="/game.svg" alt="Game Logo">
  {#if showButton}
    <button on:click={startGame}>Starte Spiel</button>
  {:else if !showDrink}
    <h2>{countdown}</h2>
  {:else}
    <h2>Trink!</h2>
  {/if}

  <div class="card-container">
    {#each cups as cup (cup.id)}
      <div class="card {cup.color}">
        <h3 contenteditable="true">Tasse {cup.id}</h3>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed sit amet semper lorem. Sed feugiat, massa a finibus aliquet, nisl nunc cursus lorem, vitae aliquam massa ante non ex.</p>
      </div>
    {/each}
  </div>
</main>
