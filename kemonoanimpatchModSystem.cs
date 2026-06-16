using System.Collections;
using System.Collections.Generic;
using System.Reflection.Emit;
using System.Reflection;
using System.Linq;
using HarmonyLib;
using kemono;
using Vintagestory.API.Client;
using Vintagestory.API.Common;
using Vintagestory.API.Config;
using Vintagestory.API.Server;
using Vintagestory.API.MathTools;
using System;

/// <summary>
/// Mod system for providing code patches to replace hardcoded bone names with vanilla-friendly ones
/// </summary>
namespace kemonoanimpatch
{
    public class kemonoanimpatchModSystem : ModSystem
    {

        // Called on server and client
        // Useful for registering block/entity classes on both sides
        public override void Start(ICoreAPI api)
        {
            var harmony = new Harmony("kemonoanimpatch");

            // Manually patch the EntityKemonoPlayerShapeRenderer lambda since it's compiler-generated
            PatchEntityKemonoPlayerShapeRendererLambda(harmony);

            // Apply all other Harmony patches in this assembly
            harmony.PatchAll();

            Mod.Logger.Notification("Kemono Animation Code Patches Loaded");
        }

        /// <summary>
        /// Uses reflection to determine the internal method name for the OverrideTesselate lambda in EntityKemonoPlayerShapeRenderer
        /// </summary>
        /// <param name="harmony">The Harmony instance to use for patching.</param>
        private void PatchEntityKemonoPlayerShapeRendererLambda(Harmony harmony)
        {
            var targetType = typeof(kemono.EntityKemonoPlayerShapeRenderer);
            
            // Find the lambda method by searching for methods with the naming pattern
            var allMethods = targetType.GetMethods(System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
            var lambdaMethod = allMethods.FirstOrDefault(m => m.Name.Contains("b__") && m.Name.Contains("OverrideTesselate"));

            if (lambdaMethod != null)
            {
                var transpilerMethod = new HarmonyMethod(typeof(EntityKemonoPlayerShapeRendererOverrideTesselatePatch).GetMethod("Transpiler"));
                harmony.Patch(lambdaMethod, transpiler: transpilerMethod);
                Mod.Logger.Notification($"Successfully patched lambda method: {lambdaMethod.Name}");
            }
            else
            {
                Mod.Logger.Warning("Could not find the OverrideTesselate lambda method to patch");
            }
        }


        public override void Dispose()
        {
            // Clean up any resources or patches when the mod is unloaded
            var harmony = new Harmony("kemonoanimpatch");
            harmony.UnpatchAll("kemonoanimpatch");
        }

    }


    /// <summary>
    /// Patches the constructor of KemonoPlayerHeadController to initialize the UpperTorsoPose and LowerTorsoPose fields with the new bone names
    /// https://gitlab.com/xeth/kemono/-/blob/1db570ed3377af43493772974e954ea87abb3377/src/Model/Animation/KemonoEntityHeadController.cs @20-122
    /// </summary>
    [HarmonyPatch(typeof(kemono.KemonoPlayerHeadController))]
    [HarmonyPatch(MethodType.Constructor)]
    [HarmonyPatch(new Type[] {typeof(IAnimationManager), typeof(EntityPlayer), typeof(Shape), typeof(string), typeof(string), typeof(string), typeof(string), typeof(string), typeof(string), typeof(EnumAxis), typeof(float), typeof(float), typeof(float)} )]
    public class KemonoPlayerHeadControllerConstructorPatch
    {
        public static void Postfix(kemono.KemonoPlayerHeadController __instance)
        {
            // Get necessary fields and properties via reflection
            var animatorField = typeof(kemono.KemonoPlayerHeadController).BaseType?.GetField("animator", BindingFlags.NonPublic | BindingFlags.Instance);
            var upperTorsoPoseField = typeof(kemono.KemonoPlayerHeadController).GetField("UpperTorsoPose", BindingFlags.NonPublic | BindingFlags.Instance);
            var lowerTorsoPoseField = typeof(kemono.KemonoPlayerHeadController).GetField("LowerTorsoPose", BindingFlags.NonPublic | BindingFlags.Instance);

            var animator = animatorField?.GetValue(__instance);
            var animatorAnimator = animator?.GetType().GetProperty("Animator", BindingFlags.Public | BindingFlags.Instance)?.GetValue(animator);

            // Re-query the poses with the new bone names
            var upperTorsoPose = animatorAnimator?.GetType().GetMethod("GetPosebyName")?.Invoke(animatorAnimator, new object[] { "UpperTorso" });
            var lowerTorsoPose = animatorAnimator?.GetType().GetMethod("GetPosebyName")?.Invoke(animatorAnimator, new object[] { "LowerTorso" });

            upperTorsoPoseField?.SetValue(__instance, upperTorsoPose);
            lowerTorsoPoseField?.SetValue(__instance, lowerTorsoPose);
        }
    }

    /// <summary>
    /// Replaces the OnFrame method in KemonoPlayerHeadController to avoid an unusual null reference exception on line 141 of the original code
    /// https://gitlab.com/xeth/kemono/-/blob/1db570ed3377af43493772974e954ea87abb3377/src/Model/Animation/KemonoEntityHeadController.cs @136-177
    /// </summary>
    [HarmonyPatch(typeof(kemono.KemonoPlayerHeadController), "OnFrame")]
    public class KemonoPlayerHeadControllerOnFramePatch
    {
        public static bool Prefix(kemono.KemonoPlayerHeadController __instance, float dt)
        {
            // Get necessary fields and properties via reflection to safely access them
            var playerField = typeof(kemono.KemonoPlayerHeadController).GetField("player", BindingFlags.NonPublic | BindingFlags.Instance);
            var entityPlayerField = typeof(kemono.KemonoPlayerHeadController).GetField("entityPlayer", BindingFlags.NonPublic | BindingFlags.Instance);
            var entityField = typeof(kemono.KemonoPlayerHeadController).GetField("entity", BindingFlags.NonPublic | BindingFlags.Instance);
            var upperTorsoPoseField = typeof(kemono.KemonoPlayerHeadController).GetField("UpperTorsoPose", BindingFlags.NonPublic | BindingFlags.Instance);
            var lowerTorsoPoseField = typeof(kemono.KemonoPlayerHeadController).GetField("LowerTorsoPose", BindingFlags.NonPublic | BindingFlags.Instance);
            var upperFootRPoseField = typeof(kemono.KemonoPlayerHeadController).GetField("UpperFootRPose", BindingFlags.NonPublic | BindingFlags.Instance);
            var upperFootLPoseField = typeof(kemono.KemonoPlayerHeadController).GetField("UpperFootLPose", BindingFlags.NonPublic | BindingFlags.Instance);
            var jointsHeadFoundProperty = typeof(kemono.KemonoPlayerHeadController).GetProperty("JointsHeadFound", BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance);
            var jointsBodyFoundProperty = typeof(kemono.KemonoPlayerHeadController).GetProperty("JointsBodyFound", BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance);

            var entityPlayer = entityPlayerField?.GetValue(__instance);
            var entity = entityField?.GetValue(__instance);
            var player = playerField?.GetValue(__instance);

            if (player == null && entityPlayer != null)
            {
                var playerProp = entityPlayer.GetType().GetProperty("Player");
                player = playerProp?.GetValue(entityPlayer);
                playerField?.SetValue(__instance, player);
            }

            var capi = (entity?.GetType().GetProperty("Api")?.GetValue(entity)) as ICoreClientAPI;

            // FIXED: Instead of calling IsSelf(capi) which throws NullReferenceException, use true
            bool isSelf = false;
            bool isSelfImmersiveFp = false;

            var upperTorsoPose = upperTorsoPoseField?.GetValue(__instance);
            var lowerTorsoPose = lowerTorsoPoseField?.GetValue(__instance);
            var upperFootRPose = upperFootRPoseField?.GetValue(__instance);
            var upperFootLPose = upperFootLPoseField?.GetValue(__instance);

            if (upperTorsoPose != null)
            {
                upperTorsoPose.GetType().GetProperty("degOffY")?.SetValue(upperTorsoPose, 0f);
                upperTorsoPose.GetType().GetProperty("degOffZ")?.SetValue(upperTorsoPose, 0f);
            }
            if (lowerTorsoPose != null)
            {
                lowerTorsoPose.GetType().GetProperty("degOffZ")?.SetValue(lowerTorsoPose, 0f);
            }
            if (upperFootRPose != null)
            {
                upperFootRPose.GetType().GetProperty("degOffZ")?.SetValue(upperFootRPose, 0f);
            }
            if (upperFootLPose != null)
            {
                upperFootLPose.GetType().GetProperty("degOffZ")?.SetValue(upperFootLPose, 0f);
            }

            bool jointsHeadFound = (bool?)jointsHeadFoundProperty?.GetValue(__instance) ?? false;
            bool jointsBodyFound = (bool?)jointsBodyFoundProperty?.GetValue(__instance) ?? false;

            if (!isSelf)
            {
                if (jointsHeadFound)
                {
                    typeof(kemono.KemonoPlayerHeadController).GetMethod("AdjustHeadTilt", BindingFlags.NonPublic | BindingFlags.Instance)?.Invoke(__instance, new object[] { dt });
                }
                if (entity?.GetType().GetProperty("BodyYawServer")?.GetValue(entity) is float bodyYawServer && bodyYawServer == 0)
                {
                    entity.GetType().GetProperty("BodyYaw")?.SetValue(entity, entity.GetType().GetProperty("Pos")?.GetValue(entity)?.GetType().GetProperty("Yaw")?.GetValue(entity.GetType().GetProperty("Pos")?.GetValue(entity)));
                }
                return false;
            }

            if (capi?.Input.MouseGrabbed ?? false)
            {
                typeof(kemono.KemonoPlayerHeadController).GetMethod("AdjustAngles", BindingFlags.NonPublic | BindingFlags.Instance)?.Invoke(__instance, new object[] { capi, dt });
            }

            if (jointsHeadFound)
            {
                typeof(kemono.KemonoPlayerHeadController).GetMethod("AdjustHeadTilt", BindingFlags.NonPublic | BindingFlags.Instance)?.Invoke(__instance, new object[] { dt });
            }

            if (isSelfImmersiveFp && jointsBodyFound)
            {
                typeof(kemono.KemonoPlayerHeadController).GetMethod("AdjustTorsoTilt", BindingFlags.NonPublic | BindingFlags.Instance)?.Invoke(__instance, new object[] { dt });
            }

            return false;
        }
    }

    /// <summary>
    /// Cleanup, no clear problems when this method is not patched for the new bone names but patching it anyway in case
    /// https://gitlab.com/xeth/kemono/-/blob/1db570ed3377af43493772974e954ea87abb3377/src/Entity/Behavior/BehaviorKemonoSkinnable.cs @1113-1237
    /// </summary>
    [HarmonyPatch(typeof(kemono.KemonoSkinnableModel), "Initialize")]
    public class KemonoSkinnableModelInitializePatch
    {
        public static bool prefix(kemono.KemonoSkinnableModel __instance)
        {
            // Get the properties via reflection
            var jointTorsoUpperProperty = typeof(kemono.KemonoSkinnableModel).GetProperty("JointTorsoUpper", BindingFlags.Public | BindingFlags.Instance);
            var jointTorsoLowerProperty = typeof(kemono.KemonoSkinnableModel).GetProperty("JointTorsoLower", BindingFlags.Public | BindingFlags.Instance);

            // Set the new bone names
            jointTorsoUpperProperty?.SetValue(__instance, "UpperTorso");
            jointTorsoLowerProperty?.SetValue(__instance, "LowerTorso");

            // Continue with the original Initialize method
            return true;
        }
    }


    /// <summary>
    /// Transpiler method for patching the OverrideTesselate method in EntityKemonoPlayerShapeRenderer
    /// Required for the arms to be visible in first-person
    /// Not called as a typical harmony patch because the method with the hardcoded strings is a lambda expression
    /// https://gitlab.com/xeth/kemono/-/blob/1db570ed3377af43493772974e954ea87abb3377/src/EntityRenderer/EntityKemonoPlayerShapeRenderer.cs @631-664
    /// </summary>
    public class EntityKemonoPlayerShapeRendererOverrideTesselatePatch
    {
        public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator generator)
        {
            var codes = new List<CodeInstruction>(instructions);
            int replacementCount = 0;

            for (int i = 0; i < codes.Count; i++)
            {
                // Replace "b_ArmUpperL" with "UpperArmL"
                if (codes[i].opcode == OpCodes.Ldstr && codes[i].operand is string str)
                {
                    if (str == "b_ArmUpperL")
                    {
                        codes[i].operand = "UpperArmL";
                        replacementCount++;
                    }
                    // Replace "b_ArmUpperR" with "UpperArmR"
                    else if (str == "b_ArmUpperR")
                    {
                        codes[i].operand = "UpperArmR";
                        replacementCount++;
                    }
                }
            }

            return codes;
        }
    }


}
