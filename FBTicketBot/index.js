require("dotenv").config();
const { 
  Client, 
  GatewayIntentBits, 
  Partials, 
  ActionRowBuilder, 
  ButtonBuilder, 
  ButtonStyle, 
  EmbedBuilder, 
  PermissionsBitField,
  ChannelType
} = require("discord.js");
const discordTranscripts = require("discord-html-transcripts");
const config = require("./config");

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers
  ],
  partials: [Partials.Message, Partials.Channel, Partials.Reaction],
  rest: { timeout: 60000 }
});

client.once("ready", () => {
  console.log(`Bot giriş yaptı: ${client.user.tag}`);
});

client.on("messageCreate", async (message) => {
  if (message.author.bot || !message.guild) return;

  if (message.content === config.prefix + "kurulum") {
    // Sadece yetkililer (Yönetici yetkisi olanlar) kurulum yapabilsin
    if (!message.member.permissions.has(PermissionsBitField.Flags.Administrator)) {
      return message.reply("Bu komutu kullanmak için `Yönetici` yetkisine sahip olmalısın.");
    }

    const embed = new EmbedBuilder()
      .setTitle("💛💙 Fenerbahçe Destek Sistemi")
      .setDescription("Destek talebi (ticket) oluşturmak için aşağıdaki butona tıklayabilirsiniz.")
      .setColor("#001e61"); // Lacivert

    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder()
        .setCustomId("open_ticket")
        .setLabel("Ticket Aç")
        .setEmoji("🎫")
        .setStyle(ButtonStyle.Primary)
    );

    await message.channel.send({ embeds: [embed], components: [row] });
    await message.delete().catch(() => {});
  }
});

client.on("interactionCreate", async (interaction) => {
  if (!interaction.isButton()) return;

  if (interaction.customId === "open_ticket") {
    // Ticket açma işlemi
    const ticketName = `ticket-${interaction.user.username}`;
    
    // Zaten açık ticket var mı kontrolü (opsiyonel ama iyi olur)
    const existingChannel = interaction.guild.channels.cache.find(c => c.name === ticketName.toLowerCase() && c.type === ChannelType.GuildText);
    if (existingChannel) {
      return interaction.reply({ content: `Zaten açık bir destek talebiniz var: ${existingChannel}`, ephemeral: true });
    }

    const permissionOverwrites = [
      {
        id: interaction.guild.id,
        deny: [PermissionsBitField.Flags.ViewChannel],
      },
      {
        id: interaction.user.id,
        allow: [PermissionsBitField.Flags.ViewChannel, PermissionsBitField.Flags.SendMessages, PermissionsBitField.Flags.ReadMessageHistory],
      },
      {
        id: client.user.id,
        allow: [PermissionsBitField.Flags.ViewChannel, PermissionsBitField.Flags.SendMessages, PermissionsBitField.Flags.ReadMessageHistory, PermissionsBitField.Flags.ManageChannels],
      }
    ];

    // Yetkili rolleri ekle
    config.staffRoles.forEach(roleId => {
      const role = interaction.guild.roles.cache.get(roleId);
      if (role) {
        permissionOverwrites.push({
          id: roleId,
          allow: [PermissionsBitField.Flags.ViewChannel, PermissionsBitField.Flags.SendMessages, PermissionsBitField.Flags.ReadMessageHistory],
        });
      }
    });

    try {
      const ticketChannel = await interaction.guild.channels.create({
        name: ticketName,
        type: ChannelType.GuildText,
        parent: config.ticketCategory !== "Kategori_ID_Gireceksiniz" ? config.ticketCategory : null,
        permissionOverwrites: permissionOverwrites
      });

      const ticketEmbed = new EmbedBuilder()
        .setTitle("Destek Talebi")
        .setDescription(`Merhaba ${interaction.user}, yetkililerimiz en kısa sürede sizinle ilgilenecektir.\nLütfen sorununuzu detaylı bir şekilde açıklayın.\n\nTalebi sonlandırmak için aşağıdaki "Kapat" butonuna tıklayabilirsiniz.`)
        .setColor("#001e61");

      const closeRow = new ActionRowBuilder().addComponents(
        new ButtonBuilder()
          .setCustomId("close_ticket")
          .setLabel("Kapat")
          .setEmoji("🔒")
          .setStyle(ButtonStyle.Danger)
      );

      await ticketChannel.send({ content: `<@${interaction.user.id}>`, embeds: [ticketEmbed], components: [closeRow] });
      await interaction.reply({ content: `Destek talebiniz oluşturuldu: ${ticketChannel}`, ephemeral: true });
    } catch (error) {
      console.error(error);
      await interaction.reply({ content: "Ticket oluşturulurken bir hata oluştu. Yetkilerimi kontrol edin.", ephemeral: true });
    }
  }

  if (interaction.customId === "close_ticket") {
    // Ticket kapatma işlemi
    await interaction.reply({ content: "Ticket kapatılıyor, transcript hazırlanıyor..." });

    try {
      const attachment = await discordTranscripts.createTranscript(interaction.channel, {
        limit: -1, 
        returnType: 'attachment',
        filename: `${interaction.channel.name}-transcript.html`,
        saveImages: true, 
        poweredBy: false
      });

      const logChannelId = config.logChannel;
      if (logChannelId && logChannelId !== "Log_Kanal_ID_Gireceksiniz") {
        const logChannel = interaction.guild.channels.cache.get(logChannelId);
        if (logChannel) {
          const logEmbed = new EmbedBuilder()
            .setTitle("Ticket Kapatıldı")
            .addFields(
              { name: "Kapatan", value: `${interaction.user} (${interaction.user.tag})`, inline: true },
              { name: "Kanal", value: interaction.channel.name, inline: true }
            )
            .setColor("Red");
          
          await logChannel.send({ embeds: [logEmbed], files: [attachment] });
        }
      }

      // Kanalı sil
      setTimeout(async () => {
        await interaction.channel.delete().catch(() => {});
      }, 3000); // 3 saniye sonra siler

    } catch (error) {
      console.error(error);
      await interaction.editReply({ content: "Kapatma işlemi sırasında bir hata oluştu." });
    }
  }
});

client.login(process.env.TOKEN);
