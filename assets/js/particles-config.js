// Function to initialize particles with the correct color based on theme
function initParticles() {
  // Check if the dark class is present on the html element
  const isDarkMode = document.documentElement.classList.contains('dark');
  const particleColor = isDarkMode ? "#ffffff" : "#000000"; // White for dark, Black for light
  const lineColor = isDarkMode ? "#ffffff" : "#000000"; // White for dark, Black for light

  // Define the configuration object dynamically
  const particlesConfig = {
    "particles": {
      "number": {
        "value": 120, // Adjusted particle count
        "density": {
          "enable": true,
          "value_area": 800
        }
      },
      "color": {
        "value": particleColor // Dynamic color
      },
      "shape": {
        "type": "circle",
        "stroke": {
          "width": 0,
          "color": "#000000" // Stroke color (can also be dynamic if needed)
        },
        "polygon": {
          "nb_sides": 5
        },
        "image": {
          "src": "img/github.svg",
          "width": 100,
          "height": 100
        }
      },
      "opacity": {
        "value": 0.3, // Adjusted opacity
        "random": false,
        "anim": {
          "enable": false,
          "speed": 1,
          "opacity_min": 0.1,
          "sync": false
        }
      },
      "size": {
        "value": 3,
        "random": true,
        "anim": {
          "enable": false,
          "speed": 40,
          "size_min": 0.1,
          "sync": false
        }
      },
      "line_linked": {
        "enable": true,
        "distance": 150,
        "color": lineColor, // Dynamic line color
        "opacity": 0.4,
        "width": 1
      },
      "move": {
        "enable": true,
        "speed": 0.5, // Adjusted speed
        "direction": "none",
        "random": false,
        "straight": false,
        "out_mode": "out",
        "bounce": false,
        "attract": {
          "enable": true, // Disabled attract for potentially better performance
          "rotateX": 600,
          "rotateY": 1200
        }
      }
    },
    "interactivity": {
      "detect_on": "canvas",
      "events": {
        "onhover": {
          "enable": true,
          "mode": "grab" // Changed hover mode
        },
        "onclick": {
          "enable": false, // Disabled click interaction
          "mode": "push"
        },
        "resize": true
      },
      "modes": {
        "grab": {
          "distance": 140, // Adjusted grab distance
          "line_linked": {
            "opacity": 1
          }
        },
        "bubble": {
          "distance": 400,
          "size": 40,
          "duration": 2,
          "opacity": 8,
          "speed": 3
        },
        "repulse": {
          "distance": 200,
          "duration": 0.4
        },
        "push": {
          "particles_nb": 4
        },
        "remove": {
          "particles_nb": 2
        }
      }
    },
    "retina_detect": true
  };

  // Initialize particles.js
  if (window.pJSDom && window.pJSDom.length > 0) {
      // If particles instance exists, destroy it first (optional, might cause flicker)
      // window.pJSDom[0].pJS.fn.vendors.destroypJS();
      // window.pJSDom = []; // Clear the array
      console.log('Particles.js instance might already exist. Re-initialization might not update colors dynamically without full reload or more complex handling.');
      // For simplicity, we assume initial load sets the color correctly.
      // A MutationObserver could be used for live updates.
  }
  particlesJS('particles-js', particlesConfig);
  console.log(`Particles initialized with color: ${particleColor}`);
}

// Run initialization when the DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initParticles);
} else {
  initParticles();
}

// Optional: Re-initialize on theme change if the theme switcher doesn't cause a page reload
// This requires knowing how the theme switcher works (e.g., event listener)
// Example using a hypothetical event 'themeChanged':
// document.addEventListener('themeChanged', initParticles);

// Example using MutationObserver (more robust for class changes):
/*
const observer = new MutationObserver((mutationsList) => {
  for(let mutation of mutationsList) {
    if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
      console.log('Theme class changed, re-initializing particles.');
      // Destroy existing instance before re-initializing (if needed)
      if (window.pJSDom && window.pJSDom.length > 0) {
        window.pJSDom[0].pJS.fn.vendors.destroypJS();
        window.pJSDom = [];
      }
      initParticles();
    }
  }
});
observer.observe(document.documentElement, { attributes: true });
*/

// Removed the commented out simpler config