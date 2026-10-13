/* Ritmika — клиентская часть: меню, появление секций, автоскрытие тостов.
   Корзина, заказы и цены считаются на сервере. */

(function () {
  'use strict';

  document.documentElement.classList.add('js');

  var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------- Шапка: рамка при скролле ---------- */

  var header = document.querySelector('[data-header]');
  var scrollTicking = false;

  function onScroll() {
    if (header) header.classList.toggle('is-scrolled', window.scrollY > 4);
    scrollTicking = false;
  }
  window.addEventListener('scroll', function () {
    if (!scrollTicking) {
      scrollTicking = true;
      requestAnimationFrame(onScroll);
    }
  }, { passive: true });
  onScroll();

  /* ---------- Мобильное меню ---------- */

  var menuBtn = document.querySelector('[data-menu-btn]');
  var menu = document.querySelector('[data-mobile-menu]');
  var menuOpen = false;
  var menuTimer = null;

  function openMenu() {
    clearTimeout(menuTimer);
    menu.hidden = false;
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { menu.classList.add('is-open'); });
    });
    menuBtn.setAttribute('aria-expanded', 'true');
    document.body.classList.add('no-scroll');
    menuOpen = true;
    var first = menu.querySelector('a');
    if (first) first.focus({ preventScroll: true });
  }

  function closeMenu(returnFocus) {
    menu.classList.remove('is-open');
    menuBtn.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('no-scroll');
    menuOpen = false;
    menuTimer = setTimeout(function () {
      if (!menu.classList.contains('is-open')) menu.hidden = true;
    }, 380);
    if (returnFocus) menuBtn.focus({ preventScroll: true });
  }

  if (menuBtn && menu) {
    menuBtn.addEventListener('click', function () {
      menuOpen ? closeMenu(false) : openMenu();
    });
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menuOpen) closeMenu(true);
    });
  }

  /* ---------- Появление секций при скролле ---------- */

  var revealEls = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  if ('IntersectionObserver' in window && !prefersReduced.matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Одна orchestrated-загрузка hero ---------- */

  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      document.documentElement.classList.add('is-loaded');
    });
  });

  /* ---------- Флеш-сообщения исчезают сами ---------- */

  var toasts = document.querySelectorAll('.toast.is-in');
  Array.prototype.forEach.call(toasts, function (el) {
    setTimeout(function () {
      el.classList.remove('is-in');
      el.classList.add('is-out');
      setTimeout(function () { el.remove(); }, 260);
    }, 3200);
  });
})();
