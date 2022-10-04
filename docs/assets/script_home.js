'use strict';
const navBar = document.querySelector('.nav__bar');

///////////////////////////////////////////////////////////////////
// Nav bar - making other links fade when hovering
const navBarHover = function (event) {
    if (event.target.classList.contains('nav__bar__link')) {
        const currentNavLink = event.target;
        const allNavLinks = currentNavLink.closest('.nav__bar').querySelectorAll('.nav__bar__link');

        allNavLinks.forEach(link => {
            if (link !== currentNavLink) link.style.opacity = this;
        });
    }
}

navBar.addEventListener('mouseover', navBarHover.bind(0.5));
navBar.addEventListener('mouseout', navBarHover.bind(1));

///////////////////////////////////////////////////////////////////
// Implementing sticky navigation bar
const header = document.querySelector('.header');
const navHeight = navBar.getBoundingClientRect().height;

const stickyNav = function (entries) {
  const [entry] = entries;
  // Sticky class must only be added if header is not intersecting with viewport
  if (!entry.isIntersecting) navBar.classList.add('sticky');
  else navBar.classList.remove('sticky');
};

const headerObserver = new IntersectionObserver(stickyNav, {
  root: null,
  threshold: 0,
  rootMargin: `-${navHeight}px`,
});

headerObserver.observe(header);

///////////////////////////////////////////////////////////////////
// Implementing tabbed component

const tab1 = document.querySelector('.program__tab--1');
const tab2 = document.querySelector('.program__tab--2');
const tab3 = document.querySelector('.program__tab--3');

const tabContent1 = document.querySelector('.tab__content--1');
const tabContent2 = document.querySelector('.tab__content--2');
const tabContent3 = document.querySelector('.tab__content--3');

const codeSample1 = document.querySelector('.code__sample--1');
const codeSample2 = document.querySelector('.code__sample--2');
const codeSample3 = document.querySelector('.code__sample--3');

// When tab 1 is clicked
tab1.addEventListener('click', function () {
    tabContent2.style.display = 'None';
    tabContent3.style.display = 'None';
    tabContent1.style.display = 'flex';
    codeSample2.style.display = 'None';
    codeSample3.style.display = 'None';
    codeSample1.style.display = 'flex';
});

// When tab 2 is clicked
tab2.addEventListener('click', function () {
    tabContent1.style.display = 'None';
    tabContent3.style.display = 'None';
    tabContent2.style.display = 'flex';
    codeSample1.style.display = 'None';
    codeSample3.style.display = 'None';
    codeSample2.style.display = 'flex';
});

// When tab 3 is clicked
tab3.addEventListener('click', function () {
    tabContent1.style.display = 'None';
    tabContent2.style.display = 'None';
    tabContent3.style.display = 'flex';
    codeSample1.style.display = 'None';
    codeSample2.style.display = 'None';
    codeSample3.style.display = 'flex';
});