/* Science of Wellness — Main JavaScript */

document.addEventListener('DOMContentLoaded', () => {
  initStars();
  initNav();
  initReveal();
});

/* Star field */
function initStars() {
  const container = document.getElementById('stars');
  if (!container) return;
  const count = 180;
  for (let i = 0; i < count; i++) {
    const star = document.createElement('div');
    star.className = 'star';
    const size = Math.random() * 2.5 + 0.5;
    star.style.cssText = `
      left: ${Math.random() * 100}%;
      top: ${Math.random() * 100}%;
      width: ${size}px;
      height: ${size}px;
      opacity: ${Math.random() * 0.6 + 0.2};
      animation-delay: ${Math.random() * 4}s;
      animation-duration: ${Math.random() * 4 + 2}s;
    `;
    container.appendChild(star);
  }
}

/* Nav scroll behavior */
function initNav() {
  const nav = document.getElementById('nav');
  if (!nav) return;
  const onScroll = () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* Hamburger (mobile) */
  const hamburger = document.getElementById('hamburger');
  if (hamburger) {
    hamburger.addEventListener('click', () => {
      document.querySelector('.nav-links')?.classList.toggle('mobile-open');
    });
  }

  /* Smooth scroll for anchor links */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

/* Intersection Observer for reveal animations */
function initReveal() {
  const elements = document.querySelectorAll('.reveal');
  if (!elements.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  elements.forEach(el => observer.observe(el));
}

/* Newsletter form */
function handleSubscribe(e) {
  e.preventDefault();
  const input = e.target.querySelector('input[type="email"]');
  const button = e.target.querySelector('button');
  if (input && button) {
    button.textContent = 'Thank you ✦';
    button.style.background = 'linear-gradient(135deg, #4A7C59, #2D5A3D)';
    input.value = '';
    input.disabled = true;
    button.disabled = true;
  }
  return false;
}
