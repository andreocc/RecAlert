document.addEventListener('DOMContentLoaded', () => {
    const updateButton = document.getElementById('update-btn');
    updateButton.addEventListener('click', atualizarDados);
    atualizarDados(); // Carrega dados iniciais
  
    async function atualizarDados() {
      let statusMessage = `Última atualização: ${new Date().toLocaleString('pt-BR')}`;
      try {
        // Tentar obter dados de clima da Open-Meteo
        let climaData;
        try {
          const climaResponse = await fetch('https://api.open-meteo.com/v1/forecast?latitude=-8.05&longitude=-34.88&hourly=temperature_2m,precipitation,relative_humidity_2m,windspeed_10m&timezone=America%2FSao_Paulo');
          if (!climaResponse.ok) throw new Error('Falha na API de clima');
          climaData = await climaResponse.json();
          localStorage.setItem('clima_data', JSON.stringify(climaData)); // Salvar no localStorage
        } catch (error) {
          console.error('Erro na API de clima:', error);
          const savedClima = localStorage.getItem('clima_data');
          if (savedClima) {
            climaData = JSON.parse(savedClima);
            statusMessage += ' (Dados salvos)';
          } else {
            climaData = await fetch('clima_fallback.json').then(res => res.json());
            statusMessage += ' (Dados estáticos)';
          }
        }
  
        // Processar dados de clima
        const now = new Date();
        const currentHourIndex = climaData.hourly.time.findIndex(t => new Date(t) >= now);
        const climaAtual = {
          temperatura: climaData.hourly.temperature_2m[currentHourIndex] || '--',
          chuva: climaData.hourly.precipitation[currentHourIndex] || '--',
          umidade: climaData.hourly.relative_humidity_2m[currentHourIndex] || '--',
          vento: climaData.hourly.windspeed_10m[currentHourIndex] || '--'
        };
        document.getElementById('temperatura').textContent = `${climaAtual.temperatura}°C`;
        document.getElementById('chuva').textContent = `${climaAtual.chuva}mm`;
        document.getElementById('umidade').textContent = `${climaAtual.umidade}%`;
        document.getElementById('vento').textContent = `${climaAtual.vento}km/h`;
  
        // Tentar obter dados de marés
        let maresData;
        try {
          const maresResponse = await fetch('mares.json');
          if (!maresResponse.ok) throw new Error('Falha ao carregar marés');
          maresData = await maresResponse.json();
        } catch (error) {
          console.error('Erro ao carregar marés:', error);
          maresData = await fetch('mares_fallback.json').then(res => res.json());
          statusMessage += ' (Marés estáticas)';
        }
        document.getElementById('mare-atual').textContent = `${maresData.mare_atual.altura}m`;
        document.getElementById('mare-status').textContent = `(${maresData.mare_atual.status})`;
        document.getElementById('proxima-mare').textContent = `${maresData.proxima_mare.tipo} ${maresData.proxima_mare.altura}m às ${maresData.proxima_mare.hora}`;
  
        // Calcular risco de alagamento
        const precip = parseFloat(climaAtual.chuva) || 0;
        const mare = parseFloat(maresData.mare_atual.altura) || 0;
        let pontos = 0;
        let motivos = [];
        if (precip > 30) { pontos += 3; motivos.push('🌧️ Chuva alta: ' + precip + 'mm'); }
        else if (precip > 10) { pontos += 1; motivos.push('🌧️ Chuva moderada: ' + precip + 'mm'); }
        if (mare > 2) { pontos += 2; motivos.push('🌊 Maré alta: ' + mare + 'm'); }
        else if (mare > 1.5) { pontos += 1; motivos.push('🌊 Maré moderada: ' + mare + 'm'); }
        if (precip > 10 && mare > 1.5) { pontos += 2; motivos.push('🌧️🌊 Combinação de chuva e maré'); }
        let risco = pontos >= 5 ? 'alto' : pontos >= 2 ? 'moderado' : 'baixo';
        document.getElementById('nivel-risco').textContent = risco.toUpperCase();
        document.getElementById('nivel-risco').className = `risco ${risco}`;
        const motivosList = document.getElementById('motivos-risco');
        motivosList.innerHTML = motivos.length ? motivos.map(m => `<li>${m}</li>`).join('') : '<li>Sem motivos significativos</li>';
  
        // Renderizar gráfico de marés (se Chart.js estiver disponível)
        const ctx = document.getElementById('chart-mare')?.getContext('2d');
        if (ctx && window.Chart) {
          if (window.mareChart) window.mareChart.destroy();
          window.mareChart = new Chart(ctx, {
            type: 'line',
            data: {
              labels: maresData.horas.map(h => h.hora),
              datasets: [{
                label: 'Altura da Maré (m)',
                data: maresData.horas.map(h => h.altura),
                borderColor: '#64B5F6',
                backgroundColor: 'rgba(100, 181, 246, 0.2)',
                fill: true
              }]
            },
            options: {
              responsive: true,
              scales: { y: { beginAtZero: true, title: { display: true, text: 'Altura (m)' } } }
            }
          });
        }
  
        // Atualizar status
        document.getElementById('last-update').textContent = statusMessage;
      } catch (error) {
        console.error('Erro crítico:', error);
        document.getElementById('last-update').textContent = `Erro ao carregar dados: ${error.message}. Usando dados estáticos.`;
      }
    }
  });