
  function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

// Usage!
sleep(3000).then(() => {
	      document.getElementById('hider').hidden = true;
    // Do something after the sleep!
});
