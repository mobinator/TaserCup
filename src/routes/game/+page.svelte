<script>
  let name = "Tasse 1";
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

  h1 {
    margin-top: 1em;
    font-size: 50pt;
    color: white;
  }
</style>

<main>
  <h1>Game Page</h1>
  <div class="card">
    <h2 contenteditable="true" bind:innerText={name}>Enter Name</h2>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed sit amet semper lorem. Sed feugiat, massa a finibus aliquet, nisl nunc cursus lorem, vitae aliquam massa ante non ex.</p>
  </div>
</main>
