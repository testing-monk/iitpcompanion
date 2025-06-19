
    const track = document.querySelector('.carousel-track');
    const slides = Array.from(track.children);
    const prevBtn = document.querySelector('.carousel-btn.prev');
    const nextBtn = document.querySelector('.carousel-btn.next');
    const dotsContainer = document.querySelector('.carousel-dots');

    let currentIndex = 0;

    // Create dots
    slides.forEach((_, index) => {
      const dot = document.createElement('span');
      dot.classList.add('dot');
      if (index === 0) dot.classList.add('active');
      dot.addEventListener('click', () => goToSlide(index));
      dotsContainer.appendChild(dot);
    });
    const dots = document.querySelectorAll('.carousel-dots .dot');

    function updateSlider() {
      track.style.transform = `translateX(-${currentIndex * 100}%)`;
      dots.forEach(dot => dot.classList.remove('active'));
      dots[currentIndex].classList.add('active');
    }

    function nextSlide() {
      currentIndex = (currentIndex + 1) % slides.length;
      updateSlider();
    }

    function prevSlide() {
      currentIndex = (currentIndex - 1 + slides.length) % slides.length;
      updateSlider();
    }

    function goToSlide(index) {
      currentIndex = index;
      updateSlider();
    }

    nextBtn.addEventListener('click', nextSlide);
    prevBtn.addEventListener('click', prevSlide);

    // Auto slide every 6 seconds
    setInterval(nextSlide, 6000);


  const mapContainer = document.getElementById('map-container');

  const googleMapEmbed = `
    <iframe
      src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3600.0820172450517!2d84.8487216753929!3d25.53564477749464!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x39ed577f6954a4ab%3A0x6ce8f1b9fc2aa02a!2sIndian%20Institute%20of%20Technology%2C%20Patna!5e0!3m2!1sen!2sin!4v1750270202620!5m2!1sen!2sin"
      width="832"
      height="500"
      style="border:0; border-radius: 10px;"
      allowfullscreen=""
      loading="lazy"
      referrerpolicy="no-referrer-when-downgrade">
    </iframe>`;

  const placeholder = `
    <img src="/static/images/map-placeholder.png" alt="Map not available" style="width:832;  border-radius: 10px;" />
  `;

  function loadMapOrPlaceholder() {
    mapContainer.innerHTML = navigator.onLine ? googleMapEmbed : placeholder;
  }

   function loadMapOrPlaceholder() {
  mapContainer.innerHTML = navigator.onLine ? googleMapEmbed : placeholder;
}

loadMapOrPlaceholder();
window.addEventListener("online", loadMapOrPlaceholder);
window.addEventListener("offline", loadMapOrPlaceholder);