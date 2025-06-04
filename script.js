document.addEventListener('DOMContentLoaded', () => {
    const updateButton = document.getElementById('update-btn');
    updateButton.addEventListener('click', atualizarDados);
    atualizarDados(); // Carrega dados iniciais ao abrir a página
  
    async function atualizarDados() {
      try {
        // Obter dados do INMET (clima)
        const dataInicio = '2025-06-03'; // Ajuste para datas atuais ou futuras
        const dataFim = '2025-06-04';
        const climaResponse = await fetch(`https://apitempo.inmet.gov.br/estacao/${dataInicio}/${dataFim}/A301`);
        const climaData = await climaResponse.json();
        const ultimoDado = climaData[climaData.length - 1];
        document.getElementById('temperatura').textContent = ultimoDado.TEM_INS || '--';
        document.getElementById('chuva').textContent = ultimoDado.CHUVA || '--';
        document.getElementById('umidade').textContent = ultimoDado.UMD_INS || '--';
        document.getElementById('vento').textContent = ultimoDado.VEN_VEL || '--';
  
        // Obter dados estáticos de marés
        const maresResponse = await fetch('mares.json');
        const maresData = await maresResponse.json();
        document.getElementById('mare-atual').textContent = maresData.mare_atual.altura;
        document.getElementById('proxima-mare').textContent = `${maresData.proxima_mare.tipo} às ${maresData.proxima_mare.hora}`;
  
        // Calcular risco de alagamento
        const precip = parseFloat(ultimoDado.CHUVA) || 0;
        const mare = parseFloat(maresData.mare_atual.altura);
        let risco = 'baixo';
        let motivos = [];
        if (precip > 30 || mare > 2) risco = 'alto';
        else if (precip > 10 || mare > 1.5) risco = 'moderado';
        if (precip > 30) motivos.push('Chuva alta');
        if (mare > 2) motivos.push('Maré alta');
        document.getElementById('nivel-risco').textContent = risco.toUpperCase();
        document.getElementById('nivel-risco').className = `risco ${risco}`;
        const motivosList = document.getElementById('motivos-risco');
        motivosList.innerHTML = motivos.map(m => `<li>${m}</li>`).join('');
  
        // Renderizar gráfico de marés
        const ctx = document.getElementById('chart-mare').getContext('2d');
        new Chart(ctx, {
          type: 'line',
          data: {
            labels: maresData.horas.map(h => h.hora),
            datasets: [{
              label: 'Altura da Maré (m)',
              data: maresData.horas.map(h => h.altura),
              borderColor: '#64B5F6',
              backgroundColor: 'transparent'
            }]
          },
          options: { scales: { y: { beginAtZero: true } } }
        });
  
        // Atualizar data e hora da última atualização
        document.getElementById('last-update').textContent = `Última atualização: ${new Date().toLocaleString('pt-BR')}`;
      } catch (error) {
        console.error('Erro ao atualizar dados:', error);
        document.getElementById('last-update').textContent = 'Erro ao carregar dados';
      }
    }
  });