using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System.Runtime.InteropServices;

namespace PhishAware.Gamification
{
    /// <summary>
    /// Mini Oyun Genel Yöneticisi (GameManager)
    /// 3 terminalin tamamlanmasını takip eder ve WebGL üzerinden FastAPI backend'ine bildirim gönderir.
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("Görev Takibi")]
        public int totalTerminals = 3;
        private int completedTerminals = 0;
        private OfficeTerminal activeTerminal;

        [Header("Arayüz Referansları")]
        [SerializeField] private GameObject inspectionModal;
        [SerializeField] private Text terminalTitleText;
        [SerializeField] private Text emailSenderText;
        [SerializeField] private Text emailSubjectText;
        [SerializeField] private Text emailBodyText;
        [SerializeField] private GameObject feedbackPanel;
        [SerializeField] private Text feedbackText;
        [SerializeField] private GameObject victoryCertificateScreen;
        [SerializeField] private Text progressText;

        [Header("Simülasyon Takip Kodu")]
        public string trackingToken = "DEMO-TOKEN";

        // WebGL JavaScript köprüsü
        [DllImport("__Internal")]
        private static extern void NotifyTrainingCompleted(string token);

        private void Awake()
        {
            if (Instance == null)
                Instance = this;
            else
                Destroy(gameObject);
        }

        private void Start()
        {
            UpdateProgressUI();
            if (inspectionModal != null)
                inspectionModal.SetActive(false);
            if (victoryCertificateScreen != null)
                victoryCertificateScreen.SetActive(false);
        }

        public void OpenEmailInspectionModal(OfficeTerminal terminal, TerminalEmailScenario scenario)
        {
            activeTerminal = terminal;
            if (inspectionModal != null)
            {
                inspectionModal.SetActive(true);
                if (terminalTitleText != null) terminalTitleText.text = scenario.terminalName;
                if (emailSenderText != null) emailSenderText.text = "Gönderen: " + scenario.sender;
                if (emailSubjectText != null) emailSubjectText.text = "Konu: " + scenario.subject;
                if (emailBodyText != null) emailBodyText.text = scenario.body;
                if (feedbackPanel != null) feedbackPanel.SetActive(false);
            }
        }

        public void SubmitVerdict(bool isPhishingSelected)
        {
            if (activeTerminal == null) return;

            bool isCorrect = (isPhishingSelected && activeTerminal.scenario.correctVerdict == EmailVerdict.Phishing) ||
                             (!isPhishingSelected && activeTerminal.scenario.correctVerdict == EmailVerdict.Clean);

            if (feedbackPanel != null)
            {
                feedbackPanel.SetActive(true);
                if (isCorrect)
                {
                    feedbackText.color = Color.green;
                    feedbackText.text = "✅ DOĞRU TESPİT!\n" + activeTerminal.scenario.explanation;
                    StartCoroutine(CompleteCurrentTerminalWithDelay());
                }
                else
                {
                    feedbackText.color = Color.red;
                    feedbackText.text = "❌ HATALI KARAR!\n" + activeTerminal.scenario.explanation + "\nLütfen e-postayı tekrar dikkatle inceleyin.";
                }
            }
        }

        private IEnumerator CompleteCurrentTerminalWithDelay()
        {
            yield return new WaitForSeconds(1.8f);
            if (inspectionModal != null)
                inspectionModal.SetActive(false);

            activeTerminal.MarkAsCompleted();
            completedTerminals++;
            UpdateProgressUI();

            if (completedTerminals >= totalTerminals)
            {
                TriggerVictory();
            }
        }

        private void UpdateProgressUI()
        {
            if (progressText != null)
                progressText.text = $"Terminaller: {completedTerminals} / {totalTerminals}";
        }

        private void TriggerVictory()
        {
            if (victoryCertificateScreen != null)
                victoryCertificateScreen.SetActive(true);

            // WebGL üzerinden PhishAware FastAPI sunucusuna başarıyı bildir
            #if UNITY_WEBGL && !UNITY_EDITOR
            NotifyTrainingCompleted(trackingToken);
            #else
            Debug.Log($"[Simülasyon Tamamlandı] Token: {trackingToken} sisteme işlendi.");
            #endif
        }
    }
}
