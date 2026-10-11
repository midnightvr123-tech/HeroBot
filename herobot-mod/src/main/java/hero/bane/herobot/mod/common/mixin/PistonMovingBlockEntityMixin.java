package hero.bane.herobot.mod.common.mixin;

import hero.bane.herobot.mod.common.bot.BotPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.piston.PistonMovingBlockEntity;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Slime-block pistons launch entities, but vanilla leaves players to their client, so a
 * server-side bot would never be launched. 26.2 flipped the {@code instanceof ServerPlayer}
 * check for bots; 26.3 no longer has that check, so the launch is applied here instead
 * (same approach as Carpet's PistonMovingBlockEntity_playerHandlingMixin).
 */
@Mixin(PistonMovingBlockEntity.class)
public class PistonMovingBlockEntityMixin {

    @Redirect(method = "moveCollidedEntities", at = @At(
            value = "INVOKE",
            target = "Lnet/minecraft/world/entity/Entity;getPistonPushReaction()Lnet/minecraft/world/level/material/PushReaction;"
    ))
    private static PushReaction launchBotPlayers(Entity entity, Level level, BlockPos pos, float progress,
                                                 PistonMovingBlockEntity piston) {
        if (entity instanceof BotPlayer && piston.getMovedState().is(Blocks.SLIME_BLOCK)) {
            Vec3 v = entity.getDeltaMovement();
            double x = v.x, y = v.y, z = v.z;
            Direction direction = piston.getMovementDirection();
            switch (direction.getAxis()) {
                case X -> x = direction.getStepX();
                case Y -> y = direction.getStepY();
                case Z -> z = direction.getStepZ();
            }
            entity.setDeltaMovement(x, y, z);
        }
        return entity.getPistonPushReaction();
    }
}
