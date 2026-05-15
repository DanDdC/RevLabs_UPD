// Variáveis globais para gerenciar o estado
let activeSlotId = null; 
let installedMods = {}; // Ex: { 'mod-1': { hp: 30, weight: 5 }, 'mod-2': ... }

const modModal = document.getElementById('mod-modal');

document.querySelectorAll('.mod-slot').forEach(slot => {
    slot.addEventListener('click', (event) => {
        activeSlotId = event.currentTarget.id;

        const rect = event.currentTarget.getBoundingClientRect();
        let topPosition = rect.bottom;
        let leftPosition = rect.left + 150;

        // Prevent the menu from going off the right side of the screen
        const modalWidth = 600; // Must match the width in your CSS
        if (leftPosition + modalWidth > window.innerWidth) {
            leftPosition = window.innerWidth - modalWidth - 20; // 20px padding from the edge
        }

        // Prevent the menu from going off the bottom of the screen
        const modalHeight = window.innerHeight * 0.5; // roughly 50vh as defined in CSS
        if (topPosition + modalHeight > window.innerHeight) {
            topPosition = rect.top - modalHeight + 40; // Pop it open ABOVE the slot instead
        }

        // Apply the calculated positions
        modModal.style.top = `${topPosition}px`;
        modModal.style.left = `${leftPosition}px`;

        modModal.showModal();
    });
});

modModal.addEventListener('click', (event) => {
    const rect = modModal.getBoundingClientRect();
    const isInDialog = (rect.top <= event.clientY && event.clientY <= rect.top + rect.height &&
                        rect.left <= event.clientX && event.clientX <= rect.left + rect.width);
    if (!isInDialog) {
        modModal.close();
        activeSlotId = null;
    }
});


document.getElementById('main-category-list').addEventListener('click', (event) => {
    if (event.target.tagName === 'LI') {
        // 1. Highlight clicked main category
        document.querySelectorAll('#main-category-list li').forEach(li => li.classList.remove('active-main'));
        event.target.classList.add('active-main');
        
        const selectedMainCat = event.target.getAttribute('data-target-main');
        const subCategories = document.querySelectorAll('#category-list li');
        let firstVisibleSubCat = null;

        // 2. Filter Column 2 (Subcategories) based on the clicked Main Category
        subCategories.forEach(subLi => {
            if (subLi.getAttribute('data-main-cat') === selectedMainCat) {
                subLi.style.display = 'block'; // Show it
                if (!firstVisibleSubCat) firstVisibleSubCat = subLi; // Remember the first one
            } else {
                subLi.style.display = 'none'; // Hide it
            }
        });

        // 3. Automatically click the first visible subcategory to update Column 3
        if (firstVisibleSubCat) {
            firstVisibleSubCat.click();
        } else {
            // Hide all parts if this category is completely empty
            document.querySelectorAll('.part-item').forEach(part => part.style.display = 'none');
        }
    }
});

document.getElementById('category-list').addEventListener('click', (event) => {
    if (event.target.tagName === 'LI') {
        // 1. Highlight clicked subcategory
        document.querySelectorAll('#category-list li').forEach(li => li.classList.remove('active-sub'));
        event.target.classList.add('active-sub');

        const targetCategory = event.target.getAttribute('data-target');
        const allParts = document.querySelectorAll('.part-item');

        // 2. Filter Column 3 (Parts) based on the clicked Subcategory
        allParts.forEach(part => {
            if (part.classList.contains(targetCategory)) {
                part.style.display = 'flex';
            } else {
                part.style.display = 'none';
            }
        });
    }
});

document.querySelector('.modal-parts-grid').addEventListener('click', (event) => {
    const partItem = event.target.closest('.part-item');
    if (!partItem || !activeSlotId) return;

    // Retrieve data from the data-* attributes
    const name = partItem.getAttribute('data-name');
    const hp = parseFloat(partItem.getAttribute('data-hp'));
    const weight = parseFloat(partItem.getAttribute('data-weight'));
    const imgUrl = partItem.getAttribute('data-img');

    // Register the part in the state
    installedMods[activeSlotId] = { hp: hp, weight: weight };

    // Update UI
    const modSlot = document.getElementById(activeSlotId);
    modSlot.classList.remove('empty');
    modSlot.classList.add('filled');
    modSlot.innerHTML = `
        <img src="${imgUrl}" class="installed-mod" alt="${name}">
        <span class="slot-label">${activeSlotId.replace('-', ' ').toUpperCase()}</span>
    `;

    recalculatePerformance();
    modModal.close();
});

function timeToSeconds(timeStr) {
    const parts = timeStr.split(':');
    const minutes = parseInt(parts[0], 10);
    const seconds = parseFloat(parts[1]);
    return (minutes * 60) + seconds;
}

function secondsToTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    
    // Format the seconds to always have 2 digits before the dot and 3 after (e.g., "05.120")
    let secondsStr = seconds.toFixed(3);
    if (seconds < 10) {
        secondsStr = '0' + secondsStr;
    }
    
    return `${minutes}:${secondsStr}`;
}

function recalculatePerformance() {
    const timeDisplay = document.getElementById('lap-time-display');
    
    const trackLengthKm = parseFloat(timeDisplay.getAttribute('data-track-length'));
    const baseSpeedKmh = parseFloat(timeDisplay.getAttribute('data-base-speed'));
    const basePower = parseFloat(timeDisplay.getAttribute('data-base-power'));
    const baseWeight = parseFloat(timeDisplay.getAttribute('data-base-weight'));

    let totalPower = basePower;
    let totalWeight = baseWeight;

    for (const slotId in installedMods) {
        totalPower += installedMods[slotId].hp;
        totalWeight += installedMods[slotId].weight;
    }

    // FÍSICA REALISTA: O limite do pneu de rua e da tração mecânica.
    let powerRatio = totalPower / basePower;
    let powerExponent = 0.30; // Ganho bom para carros fracos (ex: Fusca e Parati)

    if (basePower >= 500) {
        // Supercarros já operam no limite da aderência. 
        // Mais potência bruta tem um impacto minúsculo no tempo de volta sem instalar aerofólios e pneus slick.
        powerExponent = 0.05; 
    } else if (totalPower > 250) {
        // Carros comuns que receberam muitas peças e passaram de 250cv começam 
        // a patinar pneu em excesso na saída de curva. O ganho de tempo cai drasticamente.
        powerExponent = 0.15;
    }

    const powerMultiplier = Math.pow(powerRatio, powerExponent);
    
    // O peso, ao contrário da potência, melhora curva, aceleração e frenagem linearmente.
    const weightMultiplier = Math.pow((baseWeight / totalWeight), 0.50);
    
    const newSpeedKmh = baseSpeedKmh * powerMultiplier * weightMultiplier;
    
    const newSeconds = (trackLengthKm / newSpeedKmh) * 3600;
    const newTime = secondsToTime(newSeconds);

    timeDisplay.innerText = newTime;
    timeDisplay.classList.add('time-improved');
}
