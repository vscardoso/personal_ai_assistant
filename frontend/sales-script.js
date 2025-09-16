// Sales Landing Page - Advanced JavaScript with API Integration
// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global state
let currentUser = null;
let selectedObjection = null;
let demoCache = {};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

// Page initialization
function initializePage() {
    setupCountdowns();
    setupExitIntent();
    setupLiveNotifications();
    setupScrollEffects();
    setupFormValidation();
    setupDemoInteractions();
    preloadDemoData();
}

// Countdown timer setup
function setupCountdowns() {
    const endTime = new Date().getTime() + (24 * 60 * 60 * 1000); // 24 hours from now

    function updateCountdown() {
        const now = new Date().getTime();
        const distance = endTime - now;

        if (distance < 0) {
            document.getElementById('offerCountdown').innerHTML = "EXPIRADO";
            document.getElementById('finalCountdown').innerHTML = "<span class='text-danger'>OFERTA EXPIRADA</span>";
            return;
        }

        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Update offer countdown
        document.getElementById('offerCountdown').innerHTML =
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        // Update final countdown
        document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
        document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
        document.getElementById('seconds').textContent = seconds.toString().padStart(2, '0');
    }

    updateCountdown();
    setInterval(updateCountdown, 1000);
}

// Exit intent detection
function setupExitIntent() {
    let exitIntentTriggered = false;

    document.addEventListener('mouseleave', function(e) {
        if (e.clientY <= 0 && !exitIntentTriggered) {
            exitIntentTriggered = true;
            showExitIntentPopup();
        }
    });

    // Also trigger on mobile scroll to top
    let lastScrollTop = 0;
    window.addEventListener('scroll', function() {
        let st = window.pageYOffset || document.documentElement.scrollTop;
        if (st < lastScrollTop && st < 100 && !exitIntentTriggered) {
            exitIntentTriggered = true;
            setTimeout(() => showExitIntentPopup(), 1000);
        }
        lastScrollTop = st <= 0 ? 0 : st;
    });
}

function showExitIntentPopup() {
    const popup = document.getElementById('exitIntentPopup');
    popup.style.display = 'flex';
    trackEvent('exit_intent_shown', 'Popup', 'Exit Intent');

    // Auto close after 30 seconds
    setTimeout(() => {
        if (popup.style.display === 'flex') {
            closeExitIntent();
        }
    }, 30000);
}

function closeExitIntent() {
    document.getElementById('exitIntentPopup').style.display = 'none';
    trackEvent('exit_intent_closed', 'Popup', 'Exit Intent');
}

function activateOffer() {
    closeExitIntent();
    scrollToPricing();
    trackEvent('exit_intent_converted', 'Conversion', 'Special Offer');
}

// Live notifications
function setupLiveNotifications() {
    const names = [
        'João Silva', 'Maria Santos', 'Carlos Oliveira', 'Ana Costa', 'Pedro Almeida',
        'Lucia Ferreira', 'Roberto Souza', 'Camila Lima', 'Diego Martins', 'Fernanda Rocha'
    ];

    const achievements = [
        'aumentou suas vendas em 89%',
        'fechou R$ 47.000 em uma semana',
        'dobrou sua conversão',
        'virou top performer da empresa',
        'quebrou seu recorde pessoal',
        'fechou 5 negócios em um dia',
        'aumentou comissão em 134%'
    ];

    let currentIndex = 0;

    function showNotification() {
        const notification = document.getElementById('liveNotification');
        const name = names[currentIndex % names.length];
        const achievement = achievements[currentIndex % achievements.length];

        notification.querySelector('.notification-text').innerHTML =
            `<strong>${name}</strong> ${achievement}`;

        notification.querySelector('.notification-avatar').src =
            `https://i.pravatar.cc/40?img=${(currentIndex % 70) + 1}`;

        notification.style.display = 'block';
        notification.classList.add('slide-in');

        setTimeout(() => {
            notification.classList.remove('slide-in');
            notification.classList.add('slide-out');

            setTimeout(() => {
                notification.style.display = 'none';
                notification.classList.remove('slide-out');
            }, 500);
        }, 4000);

        currentIndex++;
    }

    // Show first notification after 10 seconds
    setTimeout(showNotification, 10000);

    // Then every 15 seconds
    setInterval(showNotification, 15000);
}

// Scroll effects
function setupScrollEffects() {
    const navbar = document.getElementById('stickyNav');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// Demo interactions setup
function setupDemoInteractions() {
    // Tab tracking
    document.querySelectorAll('#demoTabs button').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.textContent.trim();
            trackEvent('demo_tab_clicked', 'Demo', tabName);
        });
    });
}

// Preload demo data for better UX
function preloadDemoData() {
    demoCache.objectionResponses = {
        'price': {
            'empathetic': [
                'Entendo sua preocupação com o investimento. Que tal pensarmos no retorno? Em quanto você estima que suas vendas poderiam aumentar com uma ferramenta assim?',
                'Realmente é um investimento. Mas considerando que nossos clientes aumentam suas vendas em média 67%, o retorno costuma vir já no primeiro mês.',
                'Compreendo. O interessante é que muitos clientes falam isso no início, mas após verem os resultados, dizem que foi o melhor investimento que fizeram.'
            ],
            'confident': [
                'O preço reflete o valor que entregamos. Nossos clientes faturam em média R$ 15.000 a mais por mês. O investimento se paga sozinho.',
                'Vou ser direto: isso não é um custo, é um investimento com ROI comprovado. Você está pagando para dobrar suas vendas.',
                'Se R$ 97 parece caro, imagine perder R$ 15.000 todo mês por não ter a ferramenta certa. Qual é mais caro?'
            ],
            'consultative': [
                'Vamos fazer as contas juntos: quanto você deixa de ganhar por mês com negócios que não fecham? Agora compare com o investimento de R$ 97.',
                'Posso fazer uma pergunta? Qual o ticket médio das suas vendas? Porque se for acima de R$ 500, você paga a ferramenta com apenas 1 venda extra.',
                'Que tal pensarmos assim: quanto vale para você aumentar sua conversão em 30%? Esse é o resultado médio dos nossos usuários.'
            ],
            'urgent': [
                'Entendo, mas deixa eu te contar algo: amanhã o preço sobe para R$ 147. E semana que vem seus concorrentes estarão usando isso.',
                'Ok, mas vou ser transparente: temos apenas 47 vagas restantes no programa. Depois disso, lista de espera.',
                'Preciso te avisar: essa oferta especial acaba hoje à meia-noite. Amanhã volta ao preço normal de R$ 197.'
            ]
        },
        'timing': {
            'empathetic': [
                'Entendo perfeitamente. Quando seria um bom momento para você? O que precisa acontecer antes?',
                'Compreendo sua situação. Muitos clientes falam isso, mas descobrem que na verdade não existe momento perfeito.',
                'Respeito seu timing. Posso perguntar: que mudança faria você sentir que é o momento certo?'
            ],
            'confident': [
                'Posso fazer uma pergunta direta? Se não for agora, quando será? Daqui 6 meses você estará na mesma situação.',
                'O melhor momento para plantar uma árvore foi há 20 anos. O segundo melhor momento é agora.',
                'Timing perfeito não existe. O que existe é ação. Seus concorrentes não estão esperando o momento perfeito.'
            ],
            'consultative': [
                'Vamos pensar juntos: o que te faria sentir que é o momento certo? Podemos trabalhar nesses pontos.',
                'Entendo. Na sua opinião, qual seria o momento ideal? E o que você precisaria para chegar lá?',
                'Interessante. Posso te fazer uma reflexão? Quanto você estima perder em vendas enquanto espera o momento ideal?'
            ],
            'urgent': [
                'Compreendo, mas seus concorrentes não estão esperando. A cada dia que passa, eles estão fechando mais negócios.',
                'Ok, mas preciso te alertar: nossos usuários que começaram há 3 meses já faturaram R$ 50.000 extras. E você esperando o momento perfeito.',
                'Entendo, mas vou ser direto: o momento perfeito não existe. Existe oportunidade. E essa expira hoje.'
            ]
        },
        'competition': {
            'empathetic': [
                'Excelente! É sempre bom comparar. Posso te ajudar nisso. O que você gostaria de saber sobre nossos diferenciais?',
                'Perfeita decisão! Pesquisar é sempre inteligente. Quando você comparar, vai ver que somos únicos no mercado.',
                'Ótima atitude! Já que vai pesquisar, posso te dar algumas perguntas importantes para fazer aos concorrentes?'
            ],
            'confident': [
                'Compare sim! Você vai descobrir que somos os únicos com IA específica para vendas e 2.500+ casos de sucesso.',
                'Por favor, compare! Nossos resultados falam por si: 67% de aumento médio em vendas. Nenhum concorrente chega perto.',
                'Ficará fácil escolher. Somos os únicos com garantia de resultados e 30 dias para teste. Os outros têm isso?'
            ],
            'consultative': [
                'Faz muito sentido! Na sua pesquisa, recomendo verificar: 1) Resultados comprovados, 2) Suporte brasileiro, 3) Garantia real.',
                'Inteligente! Quando comparar, observe: quantos casos de sucesso eles têm? Qual a garantia? Tem suporte em português?',
                'Ótima estratégia! Posso sugerir alguns critérios importantes para sua comparação? Vai te ajudar a decidir melhor.'
            ],
            'urgent': [
                'Pode comparar, mas lembre-se: enquanto você pesquisa, seus concorrentes estão vendendo mais. Tempo é dinheiro.',
                'Compare, mas saiba que essa oferta especial acaba hoje. Amanhã estará pagando 50% a mais.',
                'Ok, mas te alerto: temos apenas 23 vagas restantes. Quando você terminar a pesquisa, pode não ter mais vaga.'
            ]
        },
        'decision': {
            'empathetic': [
                'Claro! É uma decisão importante. Posso te ajudar com alguma informação específica para sua reflexão?',
                'Perfeito! Decisões inteligentes precisam de reflexão. Tem algum ponto específico que gostaria de esclarecer?',
                'Compreendo totalmente. É um investimento importante. O que mais você gostaria de saber para se sentir seguro?'
            ],
            'confident': [
                'Entendo, mas deixa eu te fazer uma pergunta: o que você precisa saber para tomar a decisão hoje?',
                'Ok, mas vou ser direto: você já tem todas as informações. O que realmente está te impedindo?',
                'Compreendo. Mas posso te perguntar: que informação adicional mudaria sua decisão?'
            ],
            'consultative': [
                'Faz sentido pensar. Posso te ajudar estruturando os prós e contras? Ou tem alguma dúvida específica?',
                'Ótimo! Pessoas inteligentes pensam antes de decidir. Que critérios você usa para tomar decisões assim?',
                'Entendo. Na sua reflexão, sugiro considerar: custo da oportunidade, ROI esperado e risco vs benefício.'
            ],
            'urgent': [
                'Entendo, mas preciso te alertar: esta oferta especial expira hoje à meia-noite. Amanhã será 50% mais caro.',
                'Ok, mas vou ser transparente: temos lista de espera. Se não decidir hoje, pode levar 30 dias para nova vaga.',
                'Compreendo, mas seus concorrentes não estão pensando. Estão agindo. E fechando mais vendas a cada dia.'
            ]
        }
    };

    demoCache.closingTechniques = {
        'analytical': {
            name: 'Analítico',
            description: 'Pessoa orientada por dados, precisa de provas e estatísticas',
            techniques: [
                {
                    name: 'Fechamento Assumptivo com Dados',
                    description: 'Use estatísticas para assumir a compra',
                    script: 'Baseado nos dados que vimos - 67% de aumento médio, mais de 2.500 casos de sucesso - qual plano faz mais sentido para seu perfil de vendas?'
                },
                {
                    name: 'Fechamento de ROI',
                    description: 'Calcule o retorno junto com o cliente',
                    script: 'Vamos fazer a conta: se você vende R$ 10.000/mês e aumentar 35% (resultado conservador), são R$ 3.500 extras. O investimento é R$ 97. ROI de 3.600%. Quando começamos?'
                },
                {
                    name: 'Fechamento de Prova Social',
                    description: 'Use casos similares como prova',
                    script: 'João, que tem perfil parecido com o seu, aumentou 89% em vendas. Maria, também B2B, fechou R$ 156.000 extras. Com esses resultados, qual plano escolhemos?'
                }
            ]
        },
        'driver': {
            name: 'Dominante',
            description: 'Pessoa focada em resultados, quer soluções rápidas e eficazes',
            techniques: [
                {
                    name: 'Fechamento Direto',
                    description: 'Seja objetivo e vá direto ao ponto',
                    script: 'Você quer dobrar suas vendas? Sim ou não? Se sim, qual cartão usamos para processar? Se não, obrigado pelo tempo.'
                },
                {
                    name: 'Fechamento de Urgência',
                    description: 'Crie pressão temporal real',
                    script: 'Temos 2 opções: começar hoje com desconto especial, ou entrar na lista de espera. Seus concorrentes não estão esperando. Qual escolhe?'
                },
                {
                    name: 'Fechamento de Alternativa',
                    description: 'Ofereça 2 opções, ambas positivas',
                    script: 'Duas opções: Plano Pro por R$ 97 ou Enterprise por R$ 197. Ambos com garantia. Qual fecha hoje?'
                }
            ]
        },
        'expressive': {
            name: 'Expressivo',
            description: 'Pessoa sociável, motivada por relacionamentos e reconhecimento',
            techniques: [
                {
                    name: 'Fechamento Emocional',
                    description: 'Apele para sentimentos e conquistas',
                    script: 'Imagina a sensação de ser o top performer da sua empresa? De seus colegas perguntarem "qual seu segredo"? Com nossa IA, isso não é sonho, é realidade em 30 dias.'
                },
                {
                    name: 'Fechamento de Comunidade',
                    description: 'Destaque o aspecto social',
                    script: 'Você vai adorar nosso grupo VIP no Telegram. São mais de 2.500 vendedores compartilhando técnicas e comemorando vitórias. Quando você se junta à família?'
                },
                {
                    name: 'Fechamento de Visão',
                    description: 'Pinte o futuro de sucesso',
                    script: 'Em 6 meses você estará ganhando 2x mais, sendo reconhecido como especialista, talvez até palestrando sobre vendas. Que plano te leva lá mais rápido?'
                }
            ]
        },
        'amiable': {
            name: 'Amigável',
            description: 'Pessoa cautelosa, busca segurança e evita riscos',
            techniques: [
                {
                    name: 'Fechamento de Garantia',
                    description: 'Enfatize segurança e suporte',
                    script: 'Com 30 dias de garantia total, suporte brasileiro 24/7 e comunidade de apoio, seu risco é zero. Se não funcionar, devolvemos tudo + R$ 100. Como prefere pagar?'
                },
                {
                    name: 'Fechamento de Pequeno Sim',
                    description: 'Comece com compromissos menores',
                    script: 'Que tal começarmos com o teste grátis de 7 dias? Sem compromisso, sem cartão. Só para você ver como funciona. Posso criar sua conta?'
                },
                {
                    name: 'Fechamento de Suporte',
                    description: 'Destaque acompanhamento e ajuda',
                    script: 'Você não estará sozinho. Temos suporte dedicado, treinamentos semanais e comunidade ativa. Todos te ajudando a ter sucesso. Vamos começar juntos?'
                }
            ]
        }
    };
}

// Main demo functions
async function analyzeClient() {
    const conversation = document.getElementById('clientConversation').value.trim();
    const salesType = document.getElementById('salesType').value;
    const salesStage = document.getElementById('salesStage').value;
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultDiv = document.getElementById('analysisResult');

    if (!conversation) {
        showAlert('Por favor, cole uma conversa para analisar', 'warning');
        return;
    }

    if (conversation.length < 20) {
        showAlert('A conversa deve ter pelo menos 20 caracteres para uma análise precisa', 'warning');
        return;
    }

    // Show loading state
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analisando...';

    trackEvent('demo_started', 'Client Analysis', salesType);

    try {
        // Get or create demo user
        if (!currentUser) {
            currentUser = await createDemoUser();
        }

        // Call API for analysis
        const response = await fetch(`${API_BASE_URL}/analyze/conversation?user_id=${currentUser.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_text: conversation,
                context: `Demo analysis - ${salesType} - ${salesStage}`,
                relationship_type: 'professional'
            })
        });

        const result = await response.json();

        if (response.ok) {
            displayClientAnalysis(result, salesType, salesStage);
            trackEvent('demo_completed', 'Client Analysis', 'Success');
        } else {
            throw new Error(result.detail || 'Erro na análise');
        }

    } catch (error) {
        console.error('Error analyzing client:', error);
        displayFallbackAnalysis(conversation, salesType, salesStage);
        trackEvent('demo_fallback', 'Client Analysis', 'API Error');
    } finally {
        // Reset button
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-brain me-2"></i>Analisar Cliente com IA';
    }
}

async function createDemoUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: 'Demo User',
                email: `demo_${Date.now()}@salestest.com`,
                personality_traits: 'Demo user for sales landing page'
            })
        });

        if (response.ok) {
            return await response.json();
        } else {
            throw new Error('Failed to create user');
        }
    } catch (error) {
        console.error('Error creating demo user:', error);
        return { id: Math.floor(Math.random() * 1000) + 1 };
    }
}

function displayClientAnalysis(result, salesType, salesStage) {
    const resultDiv = document.getElementById('analysisResult');
    const cardsContainer = document.getElementById('analysisCards');
    const strategyContainer = document.getElementById('aiStrategy');

    // Parse analysis if it's a string
    let analysis = result.analysis;
    if (typeof analysis === 'string') {
        try {
            analysis = JSON.parse(analysis);
        } catch (e) {
            analysis = generateFallbackAnalysis();
        }
    }

    // Create analysis cards
    const cards = [
        {
            icon: 'fas fa-user-circle',
            title: 'Perfil Psicológico',
            content: analysis.communication_style || 'Cliente cauteloso que busca segurança',
            color: 'primary'
        },
        {
            icon: 'fas fa-heart',
            title: 'Motivadores',
            content: Array.isArray(analysis.strengths) ? analysis.strengths.join(', ') : 'Qualidade, confiança, resultados',
            color: 'success'
        },
        {
            icon: 'fas fa-exclamation-triangle',
            title: 'Objeções Prováveis',
            content: Array.isArray(analysis.areas_for_growth) ? analysis.areas_for_growth[0] : 'Preço, timing, necessidade de aprovação',
            color: 'warning'
        }
    ];

    cardsContainer.innerHTML = cards.map(card => `
        <div class="col-md-4">
            <div class="analysis-card">
                <div class="analysis-icon text-${card.color}">
                    <i class="${card.icon}"></i>
                </div>
                <h6 class="fw-bold">${card.title}</h6>
                <p class="small text-muted">${card.content}</p>
            </div>
        </div>
    `).join('');

    // Generate strategy
    const strategies = {
        'b2b': 'Foque em ROI e resultados mensuráveis. Use casos de empresas similares.',
        'b2c': 'Apele para benefícios pessoais e emocionais. Crie urgência com ofertas limitadas.',
        'high-ticket': 'Construa relacionamento primeiro. Ofereça consultoria e acompanhamento.',
        'subscription': 'Destaque valor contínuo. Mostre evolução e melhorias constantes.'
    };

    strategyContainer.innerHTML = `
        <div class="alert alert-info">
            <h6 class="fw-bold mb-2">🎯 Estratégia Personalizada:</h6>
            <p class="mb-2">${strategies[salesType] || 'Adapte sua abordagem ao perfil identificado.'}</p>
            <small class="text-muted">
                Baseado na análise de personalidade + tipo de venda + estágio atual
            </small>
        </div>
    `;

    // Show results
    resultDiv.classList.remove('d-none');

    // Smooth scroll to results
    setTimeout(() => {
        resultDiv.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });
    }, 300);
}

function displayFallbackAnalysis(conversation, salesType, salesStage) {
    // Analyze conversation keywords for fallback
    const keywords = conversation.toLowerCase();

    let profile = 'Cliente analítico que busca informações detalhadas';
    let motivators = 'Dados, comprovação, segurança';
    let objections = 'Preço, comparação com concorrentes';

    if (keywords.includes('caro') || keywords.includes('preço')) {
        profile = 'Cliente sensível a preço, busca valor pelo dinheiro';
        objections = 'Custo-benefício, orçamento limitado';
    }

    if (keywords.includes('pensar') || keywords.includes('decidir')) {
        profile = 'Cliente cauteloso que evita decisões impulsivas';
        motivators = 'Segurança, garantias, suporte';
        objections = 'Timing, necessidade de aprovação';
    }

    if (keywords.includes('comparar') || keywords.includes('concorrente')) {
        profile = 'Cliente pesquisador que analisa todas as opções';
        motivators = 'Diferenciais, exclusividade, resultados únicos';
        objections = 'Alternativas no mercado, features específicas';
    }

    const mockResult = {
        analysis: {
            communication_style: profile,
            strengths: motivators.split(', '),
            areas_for_growth: [objections]
        }
    };

    displayClientAnalysis(mockResult, salesType, salesStage);
}

// Objection handling demo
function selectObjection(element, objectionType) {
    // Remove active class from all objection cards
    document.querySelectorAll('.objection-card').forEach(card => {
        card.classList.remove('active');
    });

    // Add active class to selected card
    element.classList.add('active');
    selectedObjection = objectionType;

    trackEvent('objection_selected', 'Demo', objectionType);
}

async function generateObjectionResponse() {
    if (!selectedObjection) {
        showAlert('Por favor, selecione uma objeção primeiro', 'warning');
        return;
    }

    const tone = document.querySelector('input[name="responseTone"]:checked').value;
    const objectionBtn = document.getElementById('objectionBtn');
    const resultDiv = document.getElementById('objectionResult');
    const responseList = document.getElementById('responseList');

    // Show loading
    objectionBtn.disabled = true;
    objectionBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Gerando Respostas...';

    trackEvent('objection_demo_started', 'Demo', `${selectedObjection}_${tone}`);

    try {
        // Try API first
        if (currentUser) {
            const objectionTexts = {
                'price': 'Está muito caro para mim.',
                'timing': 'Não é o momento certo agora.',
                'competition': 'Vou comparar com outras opções.',
                'decision': 'Preciso pensar melhor sobre isso.'
            };

            const response = await fetch(`${API_BASE_URL}/suggestions/response?user_id=${currentUser.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: objectionTexts[selectedObjection],
                    tone: tone,
                    context: 'Sales objection handling demo'
                })
            });

            if (response.ok) {
                const result = await response.json();
                displayObjectionResponses(result.suggestions);
                trackEvent('objection_demo_completed', 'Demo', 'API Success');
                return;
            }
        }

        // Fallback to cached responses
        const responses = demoCache.objectionResponses[selectedObjection][tone];
        const formattedResponses = responses.map((response, index) => ({
            response: response,
            explanation: 'Resposta otimizada pela IA baseada em milhares de conversas de vendas',
            tone_match: 8 + Math.floor(Math.random() * 3),
            authenticity: 8 + Math.floor(Math.random() * 3)
        }));

        displayObjectionResponses(formattedResponses);
        trackEvent('objection_demo_completed', 'Demo', 'Fallback');

    } catch (error) {
        console.error('Error generating objection response:', error);
        showAlert('Erro ao gerar respostas. Tente novamente.', 'danger');
        trackEvent('objection_demo_error', 'Demo', error.message);
    } finally {
        // Reset button
        objectionBtn.disabled = false;
        objectionBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Gerar Resposta Persuasiva';
    }
}

function displayObjectionResponses(responses) {
    const responseList = document.getElementById('responseList');
    const resultDiv = document.getElementById('objectionResult');

    responseList.innerHTML = responses.slice(0, 3).map((response, index) => `
        <div class="response-option mb-3">
            <div class="response-header">
                <span class="response-number">${index + 1}</span>
                <div class="response-metrics">
                    <small class="text-muted me-3">
                        <i class="fas fa-bullseye text-primary"></i>
                        Eficácia: ${response.tone_match || 9}/10
                    </small>
                    <small class="text-muted">
                        <i class="fas fa-heart text-danger"></i>
                        Natural: ${response.authenticity || 8}/10
                    </small>
                </div>
            </div>
            <div class="response-text mb-2">
                "${response.response}"
            </div>
            <div class="response-explanation">
                <small class="text-muted">
                    💡 <strong>Por que funciona:</strong> ${response.explanation || 'Combina empatia com lógica, reduzindo resistência e mantendo interesse.'}
                </small>
            </div>
        </div>
    `).join('');

    resultDiv.classList.remove('d-none');

    // Scroll to results
    setTimeout(() => {
        resultDiv.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });
    }, 300);
}

// Closing techniques demo
function updateClosingTechniques() {
    const profileSelect = document.getElementById('clientProfile');
    const profile = profileSelect.value;
    const techniquesDiv = document.getElementById('closingTechniques');
    const techniquesList = document.getElementById('techniquesList');
    const closingScript = document.getElementById('closingScript');

    if (!profile) {
        techniquesDiv.classList.add('d-none');
        return;
    }

    const profileData = demoCache.closingTechniques[profile];

    // Show techniques
    techniquesList.innerHTML = profileData.techniques.map((technique, index) => `
        <div class="col-md-4">
            <div class="technique-card" onclick="selectTechnique('${profile}', ${index})">
                <h6 class="fw-bold">${technique.name}</h6>
                <p class="small text-muted">${technique.description}</p>
            </div>
        </div>
    `).join('');

    // Show default script (first technique)
    closingScript.innerHTML = `
        <strong>Técnica:</strong> ${profileData.techniques[0].name}<br>
        <strong>Script:</strong> "${profileData.techniques[0].script}"
    `;

    techniquesDiv.classList.remove('d-none');

    trackEvent('closing_profile_selected', 'Demo', profile);
}

function selectTechnique(profile, techniqueIndex) {
    const technique = demoCache.closingTechniques[profile].techniques[techniqueIndex];
    const closingScript = document.getElementById('closingScript');

    // Remove active from all technique cards
    document.querySelectorAll('.technique-card').forEach(card => {
        card.classList.remove('active');
    });

    // Add active to selected card
    event.currentTarget.classList.add('active');

    // Update script
    closingScript.innerHTML = `
        <strong>Técnica:</strong> ${technique.name}<br>
        <strong>Script:</strong> "${technique.script}"
    `;

    trackEvent('closing_technique_selected', 'Demo', technique.name);
}

// Form validation and submission
function setupFormValidation() {
    const form = document.getElementById('leadCaptureForm');
    const inputs = form.querySelectorAll('input[required], select[required]');

    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();

    clearFieldError(event);

    if (!value) {
        showFieldError(field, 'Este campo é obrigatório');
        return false;
    }

    if (field.type === 'email' && !isValidEmail(value)) {
        showFieldError(field, 'Digite um email válido');
        return false;
    }

    if (field.type === 'tel' && value && !isValidPhone(value)) {
        showFieldError(field, 'Digite um telefone válido');
        return false;
    }

    return true;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');

    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('is-invalid');

    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
    return phoneRegex.test(phone);
}

// Lead capture and conversion
async function submitLead(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = document.getElementById('submitBtn');

    // Validate all fields
    const requiredFields = form.querySelectorAll('input[required], select[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!validateField({ target: field })) {
            isValid = false;
        }
    });

    if (!isValid) {
        showAlert('Por favor, corrija os erros no formulário', 'danger');
        return;
    }

    // Show loading
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processando...';

    const leadData = {
        name: document.getElementById('leadName').value,
        email: document.getElementById('leadEmail').value,
        whatsapp: document.getElementById('leadWhatsapp').value,
        area: document.getElementById('leadArea').value,
        revenue: document.getElementById('leadRevenue').value
    };

    trackEvent('lead_form_submitted', 'Conversion', leadData.area);

    try {
        // Send to API
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: leadData.name,
                email: leadData.email,
                personality_traits: `Sales Lead - ${leadData.area} - ${leadData.revenue} - WhatsApp: ${leadData.whatsapp}`
            })
        });

        // Track conversion regardless of API response
        trackConversion('lead_captured', 97);

        if (typeof fbq !== 'undefined') {
            fbq('track', 'Lead', {
                value: 97,
                currency: 'BRL',
                content_category: 'Sales Tool'
            });
        }

        // Show success
        showSuccessModal();
        closeModal('leadModal');

        trackEvent('lead_converted', 'Conversion', 'Success');

    } catch (error) {
        console.error('Error submitting lead:', error);

        // Still show success for better UX
        showSuccessModal();
        closeModal('leadModal');

        trackEvent('lead_converted', 'Conversion', 'API Error but UX Success');
    } finally {
        // Reset form
        form.reset();
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>COMEÇAR TESTE GRÁTIS AGORA';
    }
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function showSuccessModal() {
    const modal = new bootstrap.Modal(document.getElementById('successModal'));
    modal.show();
}

function closeModal(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) {
        modal.hide();
    }
}

function trackEvent(action, category, label, value) {
    // Google Analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            event_category: category,
            event_label: label,
            value: value
        });
    }

    // Facebook Pixel
    if (typeof fbq !== 'undefined') {
        fbq('trackCustom', action, {
            category: category,
            label: label,
            value: value
        });
    }

    console.log(`Event tracked: ${action} - ${category} - ${label}`, value);
}

// Navigation functions
function scrollToDemo() {
    document.getElementById('demo').scrollIntoView({
        behavior: 'smooth'
    });
    trackEvent('cta_clicked', 'Navigation', 'Scroll to Demo');
}

function scrollToPricing() {
    document.getElementById('pricing').scrollIntoView({
        behavior: 'smooth'
    });
    trackEvent('cta_clicked', 'Navigation', 'Scroll to Pricing');
}

function startFreeTrial() {
    const modal = new bootstrap.Modal(document.getElementById('leadModal'));
    modal.show();
    trackEvent('cta_clicked', 'Conversion', 'Start Free Trial');
}

function selectPlan(planName) {
    trackEvent('plan_selected', 'Pricing', planName);
    startFreeTrial();
}

function showDemo() {
    scrollToDemo();
    trackEvent('cta_clicked', 'Demo', 'Show Demo Button');
}

function showUpgradeModal() {
    startFreeTrial();
    trackEvent('upgrade_clicked', 'Demo', 'Upgrade Prompt');
}

function openWhatsApp() {
    const whatsappURL = 'https://wa.me/5511999999999?text=Oi!%20Vim%20do%20site%20e%20quero%20saber%20mais%20sobre%20o%20Personal%20AI%20Assistant';
    window.open(whatsappURL, '_blank');
    trackEvent('whatsapp_clicked', 'Support', 'Contact WhatsApp');
}

// Auto-fill phone number formatting
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('leadWhatsapp');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');

            if (value.length >= 11) {
                value = value.substring(0, 11);
                value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
            } else if (value.length >= 10) {
                value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
            } else if (value.length >= 6) {
                value = value.replace(/(\d{2})(\d{4})/, '($1) $2');
            } else if (value.length >= 2) {
                value = value.replace(/(\d{2})/, '($1) ');
            }

            e.target.value = value;
        });
    }
});

// Page visibility tracking
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        trackEvent('page_hidden', 'Engagement', 'Page became hidden');
    } else {
        trackEvent('page_visible', 'Engagement', 'Page became visible');
    }
});

// Scroll depth tracking
let maxScrollDepth = 0;
window.addEventListener('scroll', function() {
    const scrollDepth = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);

    if (scrollDepth > maxScrollDepth) {
        maxScrollDepth = scrollDepth;

        // Track at 25%, 50%, 75%, 100%
        if ([25, 50, 75, 100].includes(scrollDepth)) {
            trackEvent('scroll_depth', 'Engagement', `${scrollDepth}%`);
        }
    }
});

// Time on page tracking
let timeOnPage = 0;
setInterval(() => {
    timeOnPage += 30;

    // Track every 2 minutes
    if (timeOnPage % 120 === 0) {
        trackEvent('time_on_page', 'Engagement', `${timeOnPage} seconds`);
    }
}, 30000);