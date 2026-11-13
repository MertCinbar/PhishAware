using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace PhishAware.Gamification
{
    /// <summary>
    /// PhishAware 3D Sanal Ofis - İzometrik ve Birinci Şahıs Oyuncu Kontrolcüsü (PlayerController)
    /// Çalışanın ofis içinde WASD ile gezinmesini ve terminallerle etkileşime girmesini sağlar.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class PlayerController : MonoBehaviour
    {
        [Header("Hareket Ayarları")]
        [SerializeField] private float moveSpeed = 5.0f;
        [SerializeField] private float sprintMultiplier = 1.5f;
        [SerializeField] private float rotationSpeed = 12.0f;
        [SerializeField] private float gravity = -9.81f;

        [Header("Etkileşim Ayarları")]
        [SerializeField] private float interactionRadius = 2.5f;
        [SerializeField] private LayerMask terminalLayer;
        [SerializeField] private KeyCode interactKey = KeyCode.E;

        [Header("Kamera & Mod")]
        public bool isIsometric = true;
        [SerializeField] private Camera playerCamera;

        private CharacterController characterController;
        private Vector3 velocity;
        private OfficeTerminal currentNearbyTerminal;

        void Start()
        {
            characterController = GetComponent<CharacterController>();
            if (playerCamera == null)
            {
                playerCamera = Camera.main;
            }
        }

        void Update()
        {
            HandleMovement();
            CheckForNearbyTerminals();
            HandleInteraction();
        }

        private void HandleMovement()
        {
            float horizontal = Input.GetAxisRaw("Horizontal");
            float vertical = Input.GetAxisRaw("Vertical");

            Vector3 inputDirection = new Vector3(horizontal, 0f, vertical).normalized;

            if (inputDirection.magnitude >= 0.1f)
            {
                float targetSpeed = moveSpeed * (Input.GetKey(KeyCode.LeftShift) ? sprintMultiplier : 1.0f);
                Vector3 moveDir;

                if (isIsometric)
                {
                    // İzometrik kamera açısına (45 derece) göre yön düzeltmesi
                    Matrix4x4 isoMatrix = Matrix4x4.Rotate(Quaternion.Euler(0, 45, 0));
                    moveDir = isoMatrix.MultiplyPoint3x4(inputDirection);
                }
                else
                {
                    // Standart veya birinci şahıs yönü
                    moveDir = (transform.forward * vertical + transform.right * horizontal).normalized;
                }

                characterController.Move(moveDir * targetSpeed * Time.deltaTime);

                // Karakteri hareket yönüne yumuşakça döndür
                if (moveDir != Vector3.zero)
                {
                    Quaternion targetRotation = Quaternion.LookRotation(moveDir);
                    transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, rotationSpeed * Time.deltaTime);
                }
            }

            // Yerçekimi
            if (characterController.isGrounded && velocity.y < 0)
            {
                velocity.y = -2f;
            }
            velocity.y += gravity * Time.deltaTime;
            characterController.Move(velocity * Time.deltaTime);
        }

        private void CheckForNearbyTerminals()
        {
            Collider[] hits = Physics.OverlapSphere(transform.position, interactionRadius, terminalLayer);
            if (hits.Length > 0)
            {
                OfficeTerminal terminal = hits[0].GetComponent<OfficeTerminal>();
                if (terminal != null && terminal != currentNearbyTerminal)
                {
                    currentNearbyTerminal = terminal;
                    currentNearbyTerminal.ShowInteractionPrompt(true);
                }
            }
            else if (currentNearbyTerminal != null)
            {
                currentNearbyTerminal.ShowInteractionPrompt(false);
                currentNearbyTerminal = null;
            }
        }

        private void HandleInteraction()
        {
            if (currentNearbyTerminal != null && Input.GetKeyDown(interactKey))
            {
                currentNearbyTerminal.OpenTerminalInspection();
            }
        }

        private void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.cyan;
            Gizmos.DrawWireSphere(transform.position, interactionRadius);
        }
    }
}
