<script>
  import { onMount } from 'svelte';
  import io from 'socket.io-client';

  /**
     * @type {import("socket.io-client").Socket<import("@socket.io/component-emitter").DefaultEventsMap, import("@socket.io/component-emitter").DefaultEventsMap>}
     */
  let socket;
  let connectionStatus = 'Nicht verbunden';


  let name = "Tasse 1";
  let countdown = 3;
  let showButton = true;
  let showDrink = false;
  let showDropdown = false;
  /**
     * @type {any[]}
     */
  let cups = [];

  onMount(async () => {
    connect();
  });

  function connect() {
    socket = io('http://localhost:5000');

    socket.on('connect', () => {
      connectionStatus = 'Verbunden';
      console.log("Verbindung hergestellt");
    });

    socket.on('response', (data) =>{
      console.log(`Response empfangen: ${data.data}`);
    });

    //TODO: Reset empfangen
    socket.on('reset', (data) => {
      console.log(`Reset empfangen: ${data.data}`);
      showButton = true;
      showDrink = false;
      countdown = 3;
    });
    
    //TODO: Neue Tasse empfangen
    socket.on('new_cup', (data) => {
      console.log(`Neue Tasse empfangen: ${data.data}`);
      console.log(data.data);
      cups = [...cups, data.data];
    });

    socket.on('all_cups', (data) => {
      console.log(`Neue Tassen empfangen: ${data.data}`);
      console.log(data.data);
      cups = data.data;
    });

    socket.on('cup_state', (data) => {
      console.log(`Cup Daten empfangen: ${data.data}`);
      console.log(data.data);
      let new_cup_data = data.data
      cups = cups.map(cup => {
        if(cup.id === new_cup_data.id){
          return {...cup, color: new_cup_data.color}
        }
        return cup;
      })
    });

    socket.on('disconnect', () => {
      connectionStatus = 'Getrennt';
      console.log('Verbindung getrennt');
    });

    socket.on('connect_error', (err) => {
      connectionStatus = `Verbindungsfehler: ${err.message}`;
      console.log(`Verbindungsfehler: ${err.message}`);
    });
  }

  /**
     * @param {string} message_type
     * @param {string} message
     */
  function sendMessage(message_type, message) {
    if (socket.connected) {
      socket.emit(message_type, message);
    } else {
      console.log("Socket ist nicht verbunden.");
    }
  }

  function disconnect() {
    if (socket) {
      socket.disconnect();
    }
  }

  async function startGame() {
    
    sendMessage('game_start', '3')

    showButton = false;
    const countdownInterval = setInterval(() => {
      countdown -= 1;
      if (countdown === 0) {
        clearInterval(countdownInterval);
        showDrink = true;
      }
    }, 1000);
  }

  function toggleDropdown() {
    showDropdown = !showDropdown;
  }
</script>

<style>
  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start; /* Align content to the top */
    width: 100%;
    height: 100vh;
    overflow: auto; /* Allow scrolling */
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
    flex-wrap: wrap; /* Allow the items to wrap as necessary */
    justify-content: center;
    margin-top: 5em;
    gap: 20px;
  }

  @media (max-width: 768px) {
    .card {
      width: 90%; /* Make the card take up most of the screen width */
      margin-bottom: 20px; /* Add some vertical spacing between the cards */
    }
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
      transition: background-color 0.3s ease;
    }

    button:hover {
      background-color: #f0f0f0;
    }

    .hamburger-button {
    position: absolute;
    left: 20px;
    top: 20px;
    width: 50px;
    height: 50px;
    border: 2px solid white;
    border-radius: 50%;
    background-color: transparent;
    padding: 10px;
    cursor: pointer;
  }

    img {
    width: 20rem; /* adjust as needed */
    height: auto;
    margin-top: 8rem;
    margin-bottom: 2rem;
  }

  .dropdown {
    position: absolute;
    left: 20px;
    top: 80px;
    display: flex;
    flex-direction: column;
    background-color: transparent;
    border: 2px solid white;
    border-radius: 15px;
    padding: 10px;
    gap: 0px;
    visibility: hidden;
    opacity: 0;
    transition: visibility 0s, opacity 0.5s linear;
  }

  .dropdown.visible {
    visibility: visible;
    opacity: 1;
  }

  .dropdown button {
    background-color: transparent;
    border: none;
    color: white;
    cursor: pointer;
    transition: color 0.3s ease;
  }

  .dropdown button:hover, .dropdown button:focus {
    color: #6f40ac;
  }

</style>

<main>
  <button class="hamburger-button" on:click={toggleDropdown}>
  </button>

  <div class="dropdown {showDropdown ? 'visible' : ''}">
    <button>Standard</button>
    <button>In Arbeit</button>
    <button>In Arbeit</button>
  </div>

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
        <h3 contenteditable="true">{cup.name}</h3>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed sit amet semper lorem. Sed feugiat, massa a finibus aliquet, nisl nunc cursus lorem, vitae aliquam massa ante non ex.</p>
      </div>
    {/each}
  </div>
</main>
