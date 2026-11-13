using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace PhishAware.Gamification
{
    public enum EmailVerdict
    {
        Phishing,
        Clean
    }

    [System.Serializable]
    public class TerminalEmailScenario
    {
        public string terminalName; // Örn: "Muhasebe Masası"
        public string sender;       // Örn: "muhasebe@sirket-onay-odeme.com"
        public string subject;      // Örn: "ACİL: Bekleyen Fatura & IBAN Değişikliği"
        [TextArea(4, 8)]
        public string body;
        public EmailVerdict correctVerdict;
        public string explanation;
    }

    /// <summary>
    /// Ofis masalarındaki bilgisayar terminallerini yönetir.
    /// Oyuncu yaklaştığında HUD bildirimini tetikler, incelendiğinde karar penceresini açar.
    /// </summary>
    public class OfficeTerminal : MonoBehaviour
    {
        [Header("Terminal Senaryosu")]
        public TerminalEmailScenario scenario;

        [Header("Terminal Durumu")]
        public bool isCompleted = false;

        [Header("Görsel Elementler")]
        [SerializeField] private GameObject promptCanvas;
        [SerializeField] private Light statusLight;
        [SerializeField] private Color activeColor = Color.cyan;
        [SerializeField] private Color completedColor = Color.green;

        void Start()
        {
            if (promptCanvas != null)
                promptCanvas.SetActive(false);

            if (statusLight != null)
                statusLight.color = activeColor;
        }

        public void ShowInteractionPrompt(bool show)
        {
            if (isCompleted) return;

            if (promptCanvas != null)
                promptCanvas.SetActive(show);
        }

        public void OpenTerminalInspection()
        {
            if (isCompleted) return;

            ShowInteractionPrompt(false);
            GameManager.Instance.OpenEmailInspectionModal(this, scenario);
        }

        public void MarkAsCompleted()
        {
            isCompleted = true;
            if (promptCanvas != null)
                promptCanvas.SetActive(false);

            if (statusLight != null)
                statusLight.color = completedColor;
        }
    }
}
