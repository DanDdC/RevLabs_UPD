let installedMods = {}; 

const incompatibilityMap = {
    "Twin-Scroll Turbo Kit": ["Roots Supercharger"],
    "Roots Supercharger": ["Twin-Scroll Turbo Kit"],
    "Street Coilovers": ["Fully Adjustable Race Coilovers"],
    "Fully Adjustable Race Coilovers": ["Street Coilovers"]
};

// --- SISTEMA DE POP-UP PREMIUM (HUD) ---
function showSystemModal(title, message, isConfirm, callback) {
    const modal = document.getElementById('system-modal');
    document.getElementById('system-dialog-title').innerText = title;
    document.getElementById('system-dialog-message').innerText = message;
    
    const actionsContainer = document.getElementById('system-dialog-actions');
    actionsContainer.innerHTML = ''; 

    if (isConfirm) {
        const btnCancel = document.createElement('button');
        btnCancel.className = 'btn-system cancel';
        btnCancel.innerText = 'CANCEL';
        btnCancel.onclick = () => { modal.close(); if(callback) callback(false); };

        const btnConfirm = document.createElement('button');
        btnConfirm.className = 'btn-system confirm';
        btnConfirm.innerText = 'CONFIRM';
        btnConfirm.onclick = () => { modal.close(); if(callback) callback(true); };

        actionsContainer.appendChild(btnCancel);
        actionsContainer.appendChild(btnConfirm);
    } else {
        const btnOk = document.createElement('button');
        btnOk.className = 'btn-system confirm';
        btnOk.innerText = 'OK';
        btnOk.onclick = () => { modal.close(); };
        actionsContainer.appendChild(btnOk);
    }

    modal.showModal();
}

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('mod-modal'); // Variável correta
    const addModBtn = document.getElementById('add-mod-btn');
    const mainCategories = document.querySelectorAll('#main-category-list li');
    const subCategories = document.querySelectorAll('#category-list li');
    const parts = document.querySelectorAll('.part-item');

    // Abre o menu de seleção (Centralizado com scroll seguro)
    addModBtn.addEventListener('click', () => {
        modal.style.margin = 'auto'; // Usando 'modal' em vez de 'modModal'
        modal.style.right = '0';
        modal.style.bottom = '0';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.transform = 'none';
        
        modal.showModal();
        
        const defaultTab = document.querySelector('[data-target-main="engine"]');
        if (defaultTab) defaultTab.click();
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.close();
        }
    });

    // Navegação entre abas
    mainCategories.forEach(mainLi => {
        mainLi.addEventListener('click', () => {
            mainCategories.forEach(li => li.classList.remove('active-main'));
            mainLi.classList.add('active-main');

            const targetMain = mainLi.getAttribute('data-target-main');
            subCategories.forEach(subLi => {
                if (subLi.getAttribute('data-main-cat') === targetMain) {
                    subLi.style.display = 'block';
                } else {
                    subLi.style.display = 'none';
                }
                subLi.classList.remove('active-category');
            });
            parts.forEach(part => part.style.display = 'none');
        });
    });

    subCategories.forEach(subLi => {
        subLi.addEventListener('click', () => {
            subCategories.forEach(li => li.classList.remove('active-category'));
            subLi.classList.add('active-category');

            const targetCat = subLi.getAttribute('data-target');
            parts.forEach(part => {
                if (part.classList.contains(targetCat)) {
                    part.style.display = 'flex';
                } else {
                    part.style.display = 'none';
                }
            });
        });
    });

    // Função encapsulada para instalar a peça
    function installPart(partName, hp, weight, img, mainCat) {
        const conflicts = incompatibilityMap[partName] || [];
        for (const conflictMod of conflicts) {
            if (installedMods[conflictMod]) {
                showSystemModal("INCOMPATIBILITY DETECTED", `${partName} cannot be installed alongside ${conflictMod}.`, false);
                return;
            }
        }
        installedMods[partName] = { hp, weight, img, mainCat };
        renderInstalledMods();
        modal.close();
    }

    // Processamento da Instalação da Peça
    parts.forEach(part => {
        part.addEventListener('click', () => {
            const partName = part.getAttribute('data-name');
            const addedHp = parseFloat(part.getAttribute('data-hp'));
            const addedWeight = parseFloat(part.getAttribute('data-weight'));
            const imagePath = part.getAttribute('data-img');

            const activeSubLi = document.querySelector('#category-list li.active-category');
            const mainCat = activeSubLi ? activeSubLi.getAttribute('data-main-cat') : '';

            // 1. Já instalado
            if (installedMods[partName]) {
                showSystemModal("ITEM ALREADY FITTED", `The component "${partName}" is already installed on this vehicle.`, false);
                return;
            }

            // 2. Troca de Pneus
            if (mainCat === 'tyres') {
                let existingTyre = Object.keys(installedMods).find(key => installedMods[key].mainCat === 'tyres');
                if (existingTyre) {
                    showSystemModal("TYRE CHANGE", `Vehicle is currently fitted with ${existingTyre}. Proceed with mounting ${partName}?`, true, (agreed) => {
                        if (agreed) {
                            delete installedMods[existingTyre];
                            installPart(partName, addedHp, addedWeight, imagePath, mainCat);
                        }
                    });
                    return; 
                }
            }

            installPart(partName, addedHp, addedWeight, imagePath, mainCat);
        });
    });
});

// Renderização dinâmica da lista empilhada (HTML Premium Restaurado)
function renderInstalledMods() {
    const listContainer = document.getElementById('installed-mods-list');
    listContainer.innerHTML = '';

    for (const partName in installedMods) {
        const mod = installedMods[partName];
        const row = document.createElement('div');
        row.className = 'installed-mod-row';

        const hpDisplay = mod.hp >= 0 ? `+${mod.hp} HP` : `${mod.hp} HP`;
        const weightDisplay = mod.weight >= 0 ? `+${mod.weight} KG` : `${mod.weight} KG`;

        row.innerHTML = `
            <div class="mod-left-info">
                <img src="${mod.img}" alt="${partName}" class="mod-row-img">
                <div class="mod-text-details">
                    <h4>${partName.toUpperCase()}</h4>
                    <p class="mod-short-desc">TUNING PART</p>
                </div>
            </div>
            <div class="mod-right-stats">
                <span class="stat-badge">${hpDisplay}</span>
                <span class="stat-badge">${weightDisplay}</span>
                <button class="btn-remove-mod" onclick="removeModification('${partName}')">REMOVE</button>
            </div>
        `;
        listContainer.appendChild(row);
    }

    recalculatePerformance();
}

window.removeModification = function(partName) {
    delete installedMods[partName];
    renderInstalledMods();
};

function secondsToTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    let secondsStr = seconds.toFixed(3);
    if (seconds < 10) secondsStr = '0' + secondsStr;
    return `${minutes}:${secondsStr}`;
}

function recalculatePerformance() {
    const timeDisplay = document.getElementById('lap-time-display');
    if (!timeDisplay) return;

    const trackLengthKm = parseFloat(timeDisplay.getAttribute('data-track-length'));
    const baseSpeedKmh = parseFloat(timeDisplay.getAttribute('data-base-speed'));
    const basePower = parseFloat(timeDisplay.getAttribute('data-base-power'));
    const baseWeight = parseFloat(timeDisplay.getAttribute('data-base-weight'));

    let totalPower = basePower;
    let totalWeight = baseWeight;

    for (const name in installedMods) {
        totalPower += installedMods[name].hp;
        totalWeight += installedMods[name].weight;
    }

    let powerRatio = totalPower / basePower;
    let powerExponent = basePower >= 500 ? 0.05 : (totalPower > 250 ? 0.15 : 0.30);

    const powerMultiplier = Math.pow(powerRatio, powerExponent);
    const weightMultiplier = Math.pow((baseWeight / totalWeight), 0.50);
    const newSpeedKmh = baseSpeedKmh * powerMultiplier * weightMultiplier;
    
    const newSeconds = (trackLengthKm / newSpeedKmh) * 3600;
    timeDisplay.innerText = secondsToTime(newSeconds);
}